from fastapi import APIRouter, Depends, Header, Request, Body, Response, status,HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from typing import Annotated
import json
import bcrypt
import random
from random import randrange
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import string
import asyncio
import qrcode
import io
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db.models.account import Account
from db.models.address import Address
from db.models.customer import Customer
from db.models.email import Email
from db.models.kyc import KYC
from db.models.kyc2 import KYC2
from db.models.mobile import Mobile
from db.models.notification import Notification
from db.models.password import Password
from db.models.transaction import Transaction
from db.models.sms import Sms
from db.models.emailCode import EmailCode
from db.models.token import Token
from db.models.exTransaction import TransactionRequest
from db.models.currency import Currency
from db.models.options import Options
from db.models.bioToken import Biometric
from db.models.qr import QR
from db.models.qrTerminal import QRTer
from db.models.bank import Bank
from db.models.bankBusiness import BankBusiness
from db.models.lastAccount import LastAccount
from db.models.paylink import PayLink
import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from apis.version2.middleware import DecryptRequest, decrypt_data
from pydantic import BaseModel
from db.globals.globals import tokens,smsList
import uuid

from core.hashing import Hasher

router = APIRouter()

class PaylinkCreateRequest(BaseModel):
    MerchantId: str
    API_key: str
    amount: float
    currency: str
    transactionRef: str


class PaylinkCreateResponse(BaseModel):
    paylinkID: str
    status: str


class PaylinkStatusResponse(BaseModel):
    paylinkID: str
    status: str


# Utility Functions
def validate_ip(ip_address: str) -> bool:
    # check merchant ip
    pass
    # # Placeholder for IP validation logic
    # allowed_ips = ["127.0.0.1"]  # Example of allowed IPs
    # # return ip_address in allowed_ips
    # return 1==1

def validate_merchant(merchant_id: str, api_key: str) -> bool:
    #check merchant by api key which stored in database
    # Placeholder for merchant validation logic
    # valid_merchants = {
    #     "merchant123": "secret123"
    # }
    pass
    # return valid_merchants.get(merchant_id) == api_key


async def get_client_ip(request: Request) -> str:
    # Extract client IP address
    return request.client.host


# Endpoints
@router.post("/paylink-create",)
async def create_paylink(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    # Validate IP address
    r =requests.get("http://192.223.11.185:8080/merchant", json={'id': payload["merchantID"]})
    print(r)
    r = json.loads(r.content)
    print("response:",r)
    # if not validate_ip(get_client_ip()):
    #     raise HTTPException(status_code=403, detail="Invalid IP address")
    if not payload['API_key'] == r["apiKey"]: 
        raise HTTPException(status_code=403, detail="Invalid key")
    # if not r["ip"] == request.client.host:
    #     print(r["ip"])
    #     print(request.client.host)
    #     raise HTTPException(status_code=403, detail="InvalidIP address")
    
    # Generate unique paylinkID
    paylinkID = str(uuid.uuid4())
    paylinkID = str(uuid.uuid4()).replace("-", "")[:12]
    p = PayLink(paylinkID = paylinkID,MerchantId = payload["merchantID"],amount = payload["amount"],currency=payload["amount"],transactionRefferance=payload["transactionRef"],link=f"http://192.223.11.185:4000/ecom/{paylinkID}",dateTime=datetime.now(),status="active")
    q = QRTer(terminalID = "ecom/"+paylinkID,displayName = r["merchantName"],merchantName=r["merchantName"],merchantAccount=r["merchantAccount"],currency=payload['currency'],qrStatus="pending",amount=payload["amount"],dateTime = datetime.now())
    db.add(q)
    db.add(p)
    db.commit()
    # Insert paylink record
    # paylinks_db[paylinkID] = {
    #     "MerchantId": request.MerchantId,
    #     "amount": request.amount,
    #     "currency": request.currency,
    #     "transactionRef": request.transactionRef,
    #     "date_time": datetime.now(),
    #     "status": "pending"
    # }
    transactionlink = {"link":f"http://192.223.11.185:4000/ecom/{paylinkID}"}
    return transactionlink
    
    
    
    
@router.get("/ecom/{paylink_id}")
async def connection_pay(paylink_id,db: Session = Depends(get_db)):
    # Find the related paylink
    # return paylink_id
    print(paylink_id)
    paylink = db.query(PayLink).filter(PayLink.paylinkID ==paylink_id).first()
    print(paylink)


    if not paylink:
        # paylinkID not found
        error_message = f"<h1>Error: Invalid paylinkID '{paylink_id}'</h1>"
        return HTMLResponse(content=error_message, status_code=404)

    # Generate the QR code string and image with amount included
    qr_string = f"ecom/{paylink.paylinkID}"
    qr = qrcode.make(qr_string)

    img_io = io.BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = img_io.getvalue()

    # Encode image to base64 to embed in HTML
    img_base64 = base64.b64encode(img_data).decode('utf-8')

    # Prepare the HTML response with QR code
    html_content = f"""
      <html>
          <body>
              <h1>Payment Details</h1>
              <p>Merchant Name: {paylink.MerchantId}</p>
              <p>Amount: {paylink.amount} {paylink.currency}</p>
              <p>Transaction Reference: {paylink.transactionRefferance}</p>
              <img src="data:image/png;base64,{img_base64}" alt="QR Code" />
              <p>QR Code String: <span id="qrString">{qr_string}</span></p>
              <button onclick="copyToClipboard()">Copy QR Code String</button>
              <p>Your name and email will be used together with the payment result.</p>

              <script>
                  function copyToClipboard() {{
                      var qrString = document.getElementById("qrString").innerText;
                      navigator.clipboard.writeText(qrString).then(function() {{
                          alert("QR Code String copied to clipboard!");
                      }}, function(err) {{
                          console.error("Could not copy text: ", err);
                      }});
                  }}
              </script>
          </body>
      </html>
      """

    return HTMLResponse(content=html_content)

@router.get("/status/{paylinkID}/{transactionRef}", response_model=PaylinkStatusResponse)
async def connection_status(paylinkID: str, transactionRef: str,db: Session = Depends(get_db)):
    paylink = db.query(PayLink).filter(PayLink.paylinkID ==paylinkID).first()
    if not paylink or paylink["transactionRef"] != transactionRef:
        raise HTTPException(status_code=404, detail="Paylink not found")

    return PaylinkStatusResponse(paylinkID=paylinkID, status=paylink["status"])

@router.get("/paylink")
async def getter(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    p = db.query(PayLink).filter(PayLink.link == ("http://192.223.11.185:4000/"+payload['terminalID'])).first()
    if p is None:
        return {"status_code": 401, "message": "no terminal with this id"}
    return {"status_code": 200, "message":p.MerchantId}
