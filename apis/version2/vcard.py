from fastapi import APIRouter,Depends,Header,Request,Body,Response, status
from sqlalchemy.orm import Session
from db.session import get_db
from typing import Annotated
import json
import bcrypt
import random
import pandas as pd
from random import randrange
from datetime import datetime,timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import string
import hashlib


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db.models.account import Account
from db.models.address import Address
from db.models.customer import Customer
from db.models.email import Email
from db.models.kyc import KYC
from db.models.mobile import Mobile
from db.models.notification import Notification
from db.models.password import Password
from db.models.transaction import Transaction
from db.models.sms import Sms
from db.models.emailCode import EmailCode
from db.models.token import Token
from db.models.exTransaction import TransactionRequest
from db.models.inTransaction import TransactionRequestIncoming
from db.models.fees import Fee
from db.models.bank import Bank
from db.models.currency import Currency
from db.models.bankBusiness import BankBusiness
from db.models.qr import QR
from db.models.qrTerminal import QRTer
from db.models.charge import Charge
from db.models.card import Card
from db.models.vcards import VCard
from db.models.vcard_status_log import  VCardLogs


import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

minNameLength = 3
maxNameLength = 12
passwordMax = 16
passwordMin = 8
countryCodes = {"Egypt":"+20","USA":"+1"}  # Example list of allowed countries
tokenValidMins = 150000
lvl1Max=1000
lvl2Max=10000
lvl3Max=100000
tokenLen = 16


origins = [

    "http://localhost",
    "http://localhost:8080",
]

    

class AlphanumericConverter:
    ALPHABET = 'KVEBQCUZSLFTJAIWOYNRPHXGMD'
    BASE = len(ALPHABET)
    ENCODED_LENGTH = 10

    @classmethod
    def encode(cls, number):
        binNum = format(number, '026b')
        encodedStr = ""
        for i in range(len(cls.ALPHABET)):
            if binNum[i] == "1":
                encodedStr+=cls.ALPHABET[i]
        needed = 26 -len(encodedStr)
        for i in range(needed):
            insert_position = random.randint(0, len(encodedStr))
            digit = random.randint(0,9)
            encodedStr = encodedStr[:insert_position] + str(digit) + encodedStr[insert_position:]
        return encodedStr

    @classmethod
    def decode(cls, code):
        binary_str = ""
        for char in cls.ALPHABET:
            if char in code:
                binary_str += "1"
            else:
                binary_str += "0"
        return int(binary_str, 2)
    

@router.post("/addvCard")
async def addCard(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        a = db.query(Account).filter(Account.id == payload["accountID"],Account.accountStatus == "active").first()
        c= db.query(Customer).filter(Customer.id == a.customerID).first()
        if a is None:
            return {"status_code": 401, "message": "No active account with this ID"}


        cardNum = generate_unique_cardnumber()#here code to generate 16 digit card number
        cardBr = 1
        v=db.query(VCard).filter(VCard.AccountId == a.id).first()
        if not v is None:
             return {"status_code": 401, "message": "account already has an intiated card"}


        
        ls = json.dumps({
            "singleL":1,
            "dailyL":1,
            "weeklyL":1,
            "annualL":1,
            "withdrawlL":1,
        })
        usage = json.dumps({
            "onlineUsage":False
        })
        idate = datetime.today()
        expyears= 7 #example
        edate = idate+timedelta(days= 365 * expyears)
        c = VCard(AccountId = a.id,CardNumber=cardNum,issueDate=idate,expiryDate=edate,customerName=c.firstName+" "+c.lastName,cardName=payload["cardName"],cardBrand=cardBr,cardType=payload["cardType"],status="pending",cardProfile= usage,isPhysical=payload["isPhysical"],lastTransaction=None)
        db.add(c)
        db.commit()
        db.refresh(c)
        log=VCardLogs(Card=c.id,Status="created",date_time=datetime.now())
        db.add(log)
        db.commit()
        dlast_inserted=db.query(VCard).filter(VCard.CardNumber==cardNum).first()
        return {"status_code": 201, "message": "card created successfully","card":dlast_inserted}
    except:
            message = "exception occurred with vcard"
            log(0,message)
            return {"status_code":401,"message":message}
@router.post("/changeCardStatus")
async def actCard(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.id == payload["cardID"]).first()
        if c is None:
            return {"status_code": 401, "message": "no card exists with this ID"}
        elif c.status == payload["newStatus"]:
            return {"status_code": 401, "message": "this is the current card status"}
        c = db.query(VCard).filter(VCard.id == payload["cardID"]).update({"status":payload["newStatus"]})

        db.commit()

        ###################################### edits?
        log=VCardLogs(Card=payload["cardID"],Status="activate",date_time=datetime.now())
        db.add(log)
        db.commit()
        return {"status_code": 201, "message": "card status successfully updated to "+payload["newStatus"],"card":c}
    except:
            message = "exception occurred with changing card status"
            log(0,message)
            return {"status_code":401,"message":message}





@router.get("/getCard")
async def frzCard(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.id == payload["cardID"]).first()
        if c is None:
            return {"status_code": 401, "message": "no card exists with this ID"}
        
        return {"status_code": 201, "message": c}
    except:
            message = "exception occurred with getting card"
            log(0,message)
            return {"status_code":401,"message":message}
@router.post("/updateCardService")
async def updateuseage(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.id == payload["cardID"]).first()
        if c is None:
            return {"status_code": 401, "message": "no card exists with this ID"}
        elif not c.status == "active":
            return {"status_code": 401, "message": "card not active"}
        c = db.query(VCard).filter(VCard.id == payload["cardID"]).update({"cardProfile": json.dumps({payload["service"]})})
        db.commit()
        db.refresh(c)



        return {"status_code": 201, "message": "card function updated successfully","card":c}
    except:
            message = "exception occurred with updating card"
            log(0,message)
            return {"status_code":401,"message":message}
@router.get("/getCardService")
async def updateuseage(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.id == payload["cardID"]).first()
        if c is None:
            return {"status_code": 401, "message": "no card exists with this ID"}
        



        return {"status_code": 201, "message": "card function retriever successfully","card":c}
    except:
            message = "exception occurred with getting card"
            log(0,message)
            return {"status_code":401,"message":message}
@router.post("/getCustomerCards")
async def getcustomercards(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        # payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        # payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        cards = []
        check_account=db.query(Account).filter(Account.customerID == payload["customerID"]).all()



        if len(check_account) == 0:

            return {"status_code": 201, "message": "No Account for  this Customer"}
        

        for account in check_account:

            for c in db.query(VCard).filter(VCard.AccountId == account.id).all():
                        cards.append((c))
        if len(cards)> 0:
            return {"status_code": 201, "message": cards}

        else:
            return {"status_code": 201, "message": []}
    except:
        message = "exception occurred with getting card"
        log(0,message)
        return {"status_code":401,"message":message}


@router.post("/getaccountCards")
async def getAllCardsRelatedToAccount(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.AccountId == payload['AccountId']).all()
        return {"status_code": 201, "message": c}
    except:
            message = "exception occurred with getting card"
            log(0,message)
            return {"status_code":401,"message":message}
@router.post("/getaccountCard")
async def getAllCardsRelatedToAccount(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.id == payload['cardID']).first()
        a= db.query(Account).filter(Account.id == c.AccountId).first()
        return {"status_code": 201, "message": a}
    except:
            message = "exception occurred with getting card"
            log(0,message)
            return {"status_code":401,"message":message}
    
@router.post("/getaccountNumber")
async def getAllCardsRelatedToAccount(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        c = db.query(VCard).filter(VCard.CardNumber == payload['cardNumber']).first()
        a= db.query(Account).filter(Account.id == c.AccountId).first()
        return {"status_code": 201, "message": a}
    except:
            message = "exception occurred with getting number"
            log(0,message)
            return {"status_code":401,"message":message}

def generate_unique_cardnumber():
    new_card=''.join(random.choices('0123456789', k=14))
    return new_card

def log(logFile,message):
    #error,transaction,login
    if logFile == 0:
        fileName = "logs/errors.txt"
    if logFile == 1:
        fileName = "logs/transactions.txt"
    if logFile == 2:
        fileName = "logs/login.txt"

    file_object = open(fileName,'a')
    file_object.write(message+'\n')
    file_object.close()
    return True
