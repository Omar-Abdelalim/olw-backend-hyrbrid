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

import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from apis.version2.middleware import DecryptRequest, decrypt_data
from pydantic import BaseModel
from db.globals.globals import tokens,smsList,currentServer,currentPort

from core.hashing import Hasher

router = APIRouter()

minNameLength = 3
maxNameLength = 12
passwordMax = 16
passwordMin = 8
countryCodes = {"Egypt": "+20", "USA": "+1"}  # Example list of allowed countries
tokenValidMins = 150000
codeValidMinutes = 5
session_expiry_time = 10

origins = [

    "http://localhost",
    "http://localhost:8080",
]

def preprocess():
    return {"status_code": 201, "message": ""}

@router.post("/checkPhone")
async def reg1(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        ph = db.query(Mobile).filter(Mobile.mobileNumber == payload["mobileNumber"],Mobile.countryCode == payload["countryCode"],Mobile.numberStatus == "active").first()
        if ph is None:
            return {"status_code": 201, "message": "phone number available"}
        return {"status_code": 401, "message": "phone Already Exsit"}
    except:
        message = "exception occured with checking phone"
        log(0, message)
        return {"status_code": 401, "message": message}
@router.post("/merchantAccount")
async def regMer(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    # try:
        payload = await request.body()
        payload = json.loads(payload)
        e = db.query(Customer).filter(Customer.email == payload["email"]).first()
        if not e is None:
            return {"status_code": 402, "message": "email already taken by another customer"}
        e = db.query(Customer).filter(Customer.phoneNumber == payload["phoneNumber"],Customer.countryCode == payload["countryCode"]).first()
        if not e is None:
            return {"status_code": 402, "message": "phone number already taken by another customer"}
        c = Customer(firstName = payload["firstName"],customerNumber = "0",lastName = payload["lastName"],email = payload["email"],birthdate=payload["birthDate"],customerStatus = "third level",phoneNumber=payload["phoneNumber"],countryCode=payload["countryCode"],pin=payload["pin"],IDIqama=payload["IDIqama"])
        
        db.add(c)
        db.commit()
        cus = db.query(Customer).filter(Customer.email == c.email).first()
        e = Email(customerID = cus.id,dateTime = datetime.now(),emailStatus = "active",emailAddress = cus.email)
        m = Mobile(customerID = cus.id,dateTime = datetime.now(),numberStatus = "active",mobileNumber = payload["phoneNumber"],countryCode = payload["countryCode"])
        p = Password(customerID = cus.id,dateTime = datetime.now(),passwordStatus = "active",passwordHash = newPassword(payload["password"]))
        db.add(e)
        db.add(m)
        db.add(p)
        db.query(Customer).filter(Customer.email == c.email).update({"customerNumber":str(cus.id).zfill(9)})
        cur = db.query(Currency).filter(
                Currency.country == payload["country"] and Currency.currencyName == payload["currency"]).first()
        if cur is None:
            return {"status_code": 401, "message": "currency doesn't exist in currency table"}

        bAccount = generate_bank_account(db,currency_code=cur.code)
        if not bAccount["status_code"] == 201:
            return bAccount
        account = {"accountNumber": bAccount["message"], "accountType": "eWallet",
                    "balance": 100, "country": "USA", "currency": "USD", "friendlyName": "primary"}

        acco = addAccnt(cus.id, account["accountNumber"], account["accountType"], account["balance"], "active", True,
                        db, account["country"], account["currency"], "primary","IEOLW"+account['accountNumber'],"IEOLW","xyz 123","One Link Wallet","Dublin, Ireland")
        if not acco["status_code"] == 201:
            return acco
        db.commit()
        
        return {"status_code":200,"message":"account added","accountNumber":account["accountNumber"]}
    # except:
    #     message = "exception occured with creating customer"
    #     log(0, message)
    #     return {"status_code": 401, "message": message}

@router.post("/handshake")
async def handshake(request: Request, response: Response, data: DecryptRequest, db: Session = Depends(get_db)):
    b = await request.body()
    payload = json.loads(b)

    print("payload",payload)
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    ip = x_forwarded_for
    if not x_forwarded_for :
        ip = request.client.host
    key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    keys = tokens.keys()
    while key in keys:
        key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    tokens[key] = {'key': payload['message'],'ip':ip, 'exp': datetime.now() + timedelta(minutes=session_expiry_time),'customerID':None}
    return {"status_code":200,"message":"Hand Shake Successful","session key":key}




@router.post("/reg1")
async def reg1(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    payload = await request.body()
    payload = json.loads(payload)
    # payload = payload['message']
    # payload = json.loads(payload)
    token = payload['token']


    print('payload:',payload)
    password = payload["password"]
    c = Customer(firstName=payload["firstName"],
                 lastName=payload["lastName"],
                 email=payload["email"],
                 customerStatus="pending",
                 IDIqama=payload["ID/Iqama"],
                 phoneNumber=payload["mobileNumber"],
                 countryCode=payload["countryCode"],
                 customerNumber = '0'
                 )

    if len(c.firstName) < minNameLength or len(c.lastName) < minNameLength or len(c.firstName) > maxNameLength or len(
            c.lastName) > maxNameLength:
        return {"status_code": 401,
                "message": "First or Last Name invalid, please type in your first and last names between " + str(
                    minNameLength) + " and " + str(maxNameLength) + " characters"}

    if len(c.email) < minNameLength:
        return {"status_code": 401, "message": "address too short"}
    checkemailexsit = db.query(Customer).filter(Customer.email == c.email).first()
    checkemailexsit2 = db.query(Email).filter(Email.emailAddress == c.email).first()
    checkPhone = db.query(Customer).filter(Customer.countryCode == payload["countryCode"],Customer.phoneNumber == payload["mobileNumber"]).first()
    if not(checkemailexsit is None and checkemailexsit2 is None):
        return {"status_code": 401, "message": "Email Already Exsit"}
    phone = db.query(Mobile).filter(Mobile.countryCode == payload["countryCode"],Mobile.mobileNumber == payload["mobileNumber"],Mobile.numberStatus == "active").first()
    if not (phone is None and checkPhone is None):
        return {"status_code": 401, "message": "This phone number is already linked to a user, please use another one"}
    passcur = newPassword(password)
    if not passcur:
        return {"status_code": 401, "message": "please pick a password between 8 and 16 "}

    birthdate = datetime.strptime(payload["birthDate"], '%d/%m/%Y')
    age = is_18_or_older(birthdate)
    if not age:
        return {"status_code": 401, "message": "you have to be 18 years or older to create an account"}
    c.birthdate = birthdate

    # try:
    db.add(c)
    db.commit()
    db.refresh(c)
    if c.customerStatus == "pending":
        if not True :#FOCAL SANCTION LISTING
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 301 customer await compliance team response (Focal Sanction)")
            return {"status_code":301,"message":"your request is being reviewed, this might take up to one working day"}
        db.query(Customer).filter(Customer.id == c.id).update({"customerStatus":"Fapproved"})
        db.commit()
        db.refresh(c)

    if c.customerStatus == "Fapproved":
        if not True :#risk assessment
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 301 customer await compliance team response (risk assessment)")
            return {"status_code":301,"message":"your request is being reviewed, this might take up to one working day"}
        db.query(Customer).filter(Customer.id == c.id).update({"customerStatus":"Rapproved"})
        db.commit()
        db.refresh(c)

    if c.customerStatus == "Rapproved":
        if not True :#nafath
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 302 customer failed Nafath screening")
            return {"status_code":301,"message":"We cannot verify your identity\nWe are sorry, we cannot confirm your identity as with your National ID and your Mobile number."}
        db.query(Customer).filter(Customer.id == c.id).update({"customerStatus":"approved"})
        db.commit()
        db.refresh(c)

    # except:
    #     message = "exception occured with creating customer"
    #     log(0, message)
        # return {"status_code": 401, "message": message}
    try:
        cus = db.query(Customer).filter(Customer.email == c.email).first()

        p = Password(passwordHash=passcur, passwordStatus="active", customerID=cus.id, dateTime=datetime.now())
        confirmationCode = send_template_email(c.email, 1, cus)

        ec = EmailCode(customerID=cus.id, dateTime=datetime.now(), code=confirmationCode, email=c.email,

                       expiration=datetime.now() + timedelta(minutes=codeValidMinutes), result="pending")

        notif = createNotif(db,c.id,"Please Confim Email Address","email registeration",f"http://{currentServer}:4000/resendVer")

        db.add(ec)
        cNum = str(cus.id).zfill(9)
        if payload["terminal"] >0:
            cNum+="-"+int(payload["terminal"]).zfill(3)
        db.query(Customer).filter(Customer.email == c.email).update({"emailCode": confirmationCode})
        db.query(Customer).filter(Customer.email == c.email).update({"customerNumber":str(cus.id).zfill(9)})
        db.add(p)

        addSMS(cus.id, payload["mobileNumber"], payload["countryCode"], db)
        cur = db.query(Currency).filter(
            Currency.country == payload["country"] and Currency.currencyName == payload["currency"]).first()
        if cur is None:
            return {"status_code": 401, "message": "currency doesn't exist in currency table"}
        bAccount = generate_bank_account(db,currency_code=cur.code)
        if not bAccount["status_code"] == 201:
            return bAccount
        account = {"accountNumber": bAccount["message"], "accountType": "eWallet",
                   "balance": 100, "country": "USA", "currency": "USD", "friendlyName": "primary"}

        acco = addAccnt(cus.id, account["accountNumber"], account["accountType"], account["balance"], "active", True,
                        db, account["country"], account["currency"], "primary","IEOLW"+account['accountNumber'],"IEOLW","xyz 123","One Link Wallet","Dublin, Ireland")
        if not acco["status_code"] == 201:
            return acco
        db.commit()
        db.refresh(ec)
        db.refresh(p)
    except:
        message = "exception occurred with sending sms and email or with creating account"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Welcome to Saudi Wallet"}


@router.post("/reg2")
async def reg2(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        kycO = db.query(KYC).filter(KYC.customerID == payload["id"], KYC.kycStatus == "active")
        if kycO.first() is not None:
            db.query(KYC).filter(KYC.customerID == payload["id"]).update({"kycStatus": "outdated"})
            # db.refresh()

        addO = db.query(Address).filter(Address.customerID == payload["id"], Address.addressStatus == "active")
        if addO.first() is not None:
            db.query(Address).filter(Address.customerID == payload["id"]).update({"addressStatus": "outdated"})
            # db.commmit()

        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if not cus:
            return {"status_code": 400, "message": "no customer with this id"}
        ee = db.query(Email).filter(Email.customerID == payload["id"] and Email.emailStatus == "active").first()
        # mm = db.query(Mobile).filter(Mobile.customerID == payload["id"] and Mobile.numberStatus == "active").first()
        mm = True
        if ee is None or mm is None:
              print("email:",ee)
              print("phone:",mm)
              return {"status_code": 400, "message": "email or phone not verified"}
        kyc = KYC(firstName=cus.firstName, familyName=cus.lastName, customerID=cus.id, birthDate=cus.birthdate)
        kyc.fullAddress = payload["address"]
        kyc.residenceCountry = payload["countryOfResidence"]
        kyc.birthCountry = payload["countryOfCitzenship"]
        kyc.kycStatus = "active"

        address = Address(customerID=cus.id, addressStatus="active", address1=kyc.fullAddress,
                          country=kyc.residenceCountry, dateTime=datetime.now())
        address.city = payload["city"]
        address.zipCode = payload["postalCode"]
        address.addressStatus = "active"

        if not (payload["address"] and payload["city"] and payload["postalCode"]):
            return False, "Address, city, and postal code are required fields."

        def is_valid_postal_code(code, country):  # dummy function for now
            return True

        # Validate postal code format (hypothetical example)
        if not is_valid_postal_code(payload["postalCode"], payload["countryOfResidence"]):
            return False, "Invalid postal code format for the selected country."

        

        # if not countryCodes[payload["countryOfResidence"]] == payload["countryCode"]:
        #     return False, "country code doesn't match your country of residence"

        db.add(kyc)
        db.add(address)
        db.query(Customer).filter(Customer.id == payload["id"]).update({"customerStatus": "second level"})
        db.commit()
        db.refresh(kyc)
        db.refresh(address)
    except:
        message = "exception occurred with creating kyc and address"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Account successfully upgraded"}

@router.post("/reg3")
async def reg3(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        beforep = preprocess()
        if not beforep["status_code"] == 201:
            return beforep
        kyc0 = db.query(KYC2).filter(KYC2.customerID == payload["id"], KYC2.kycStatus == "active")
        kyc1 = db.query(KYC).filter(KYC.customerID == payload["id"], KYC.kycStatus == "active")
        
        if kyc1.first() is None:
            return {"status_code": 400, "message":"please make sure the first kyc is completed first"}
        
        if kyc0.first() is not None:
            db.query(KYC2).filter(KYC2.customerID == payload["id"]).update({"kycStatus": "outdated"})
            # db.refresh()

        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if not cus:
            return {"status_code": 400, "message": "no customer with this id"}
        
        kyc = KYC2(customerID=cus.id, incomeRange=payload["incomeRange"],profession=payload["profession"],sourceOfIncome=payload["sourceOfIncome"],employment=payload["employment"],kycStatus="active")
        
        
        db.add(kyc)
        db.query(Customer).filter(Customer.id == payload["id"]).update({"customerStatus": "third level"})
        db.commit()
        db.refresh(kyc)
    except:
        message = "exception occurred with creating kyc2"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Account successfully upgraded"}



@router.post("/confirmEmail")
async def sendemail1(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        payload = json.loads(payload)
        

        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.email == payload["email"]).first()

        if cus is None:
            return "no customer exists with this email"

        e = Email(emailAddress=payload["email"], emailStatus="active", customerID=cus.id, dateTime=datetime.now())

        db.query(Customer).filter(Customer.email == payload["email"]).update({"customerStatus": "first level"})

        db.add(e)
        db.commit()
        db.refresh(e)
    except:
        message = "exception occurred with creating email"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "email Succefully added"}


@router.post("/confirmMobile")
async def sendSms(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        payload = json.loads(payload)
    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()

        if cus is None:
            return "no customer exists with this id"

        n = Mobile(mobileNumber=payload["mobileNumber"], countryCode=payload["countryCode"], numberStatus="active",
                   customerID=cus.id, dateTime=datetime.now())

        db.query(Customer).filter(Customer.id == payload["id"]).update(
            { "smsCode": "-1"})

        db.add(n)
        db.commit()
        db.refresh(n)

    except:
        message = "exception occurred with creating mobile"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "mobile Succefully added"}


@router.post("/pinLogin")
async def pinLogin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        if cus.pin is None:
            return {"status_code": 401, "message": "customer has no pin yet"}
        pin = cus.pin
        if pin == payload["pin"]:
            tokens[token]['id'] = cus.id
            return {"status_code": 201, "message": "Correct Pin", "token": token,"pin":pin}

        return {"status_code": 402, "message": "wrong pin"}
    except:
        message = "exception occurred with checking pin"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.put("/pin")
async def changePin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}

        pin = cus.pin

        if pin == payload["pin"]:
            db.query(Customer).filter(Customer.id == payload["id"]).update({"pin": payload["newPin"]})
            db.commit()

            return {"status_code": 201, "message": "pin has been updated", "token": token}

        return {"status_code": 401, "message": "Incorrect Pin"}
    except:
        message = "exception occurred with checking pin"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.put("/email")
async def changeEmail(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        oldE = db.query(Email).filter(Email.emailAddress == payload["email"], Email.emailStatus == "active").first()
        if not oldE is None:
            return {"status_code": 401, "message": "email already used"}

        confirmationCode = send_template_email(payload["email"], 3, cus)
        updateEmail = send_template_email(cus.email,4,cus)
        db.query(EmailCode).filter(EmailCode.customerID == cus.id,EmailCode.result == "pending").update({"result":"expired"})

        ec = EmailCode(customerID=cus.id, dateTime=datetime.now(), code=confirmationCode, email=payload["email"],
                       expiration=datetime.now() + timedelta(minutes=codeValidMinutes), result="pending")
        db.query(Customer).filter(Customer.id == payload["id"]).update({"emailCode": ec.code})
        db.query(Notification).filter(Notification.customerID==cus.id, Notification.notificationType=="email update").update({"notificationStatus":"expired"})
        notif = createNotif(db,cus.id,"Please Confirm Your Email Update","email update",f"http://{currentServer}:4000/resendUpdateVer")

        db.add(ec)
        db.commit()
         

        return {"status_code": 201, "message": "update email sent", "token": token}


    except:
        message = "exception occurred with checking email"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.put("/phone")
async def changePhone(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}

        confirmationCode = addSMS(cus.id, payload["mobileNumber"], payload["countryCode"], db)

        return {"status_code": 201, "message": confirmationCode, "token": token}


    except:
        message = "exception occurred with checking email"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.put("/password")
async def changePhone(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}


        
        if not cus.pin == payload["pin"]:
            return {"status_code": 401, "message": "incorrect pin number"}
        passcur = newPassword(payload["password"])
        if not passcur:
            return {"status_code": 401, "message": "please pick a password between 8 and 16 "}
        p = Password(passwordHash=passcur, passwordStatus="active", customerID=cus.id, dateTime=datetime.now())
        db.add(p)
        db.query(Password).filter(Password.customerID == payload["id"]).update({"passwordStatus": "outdated"})
        db.commit()

        return {"status_code": 201, "message": "password updated", "token": token}


    except:
        message = "exception occurred with checking email"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/createPin")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        if not payload["pin1"] == payload["pin2"]:
            return {"status_code": 401, "message": "Please ensure Pin entries are matching"}

        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        pincurr = str(payload["pin1"])

        res = db.query(Customer).filter(Customer.id == payload["id"]).update({"pin": pincurr})
        db.commit()
     

    except:
        message = "exception occurred with creating pin"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "PIN successfully created ", "token": token}

@router.post("/createBio")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        b = Biometric(customerID = payload["id"],dateTime= datetime.now(),pin=str(payload["pin"]),phoneID=payload["phoneID"])

        db.add(b)
        db.commit()
         

    except:
        message = "exception occurred with creating Bio pin"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Biometric token stored", "token": token}

@router.get("/bioPin")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        b = db.query(Biometric).filter(Biometric.phoneID == payload["phoneID"]).first()

    except:
        message = "exception occurred with getting Bio pin"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": b.pin, "token": token}

@router.post("/createQR")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").first()
        if not qr is None:
            return {"status_code": 401, "message": "user has active QR request"}
        q = QR(customerID = payload["id"],dateTime= datetime.now(),accountNo=payload["accountNumber"],currency=payload["currency"],amount=payload["amount"],qrStatus="pending")

        db.add(q)
        db.commit()
         

    except:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "QR request generated", "token": token}

@router.post("/createQRTer")
async def createQrTer(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    # try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        # token = payload['token']
        r =requests.get(f"http://{currentServer}:8080/terminal", json={'id': payload["terminalID"]})
        r = json.loads(r.content)
        if not r["status_code"] == 200:
            return r
        
        mName = r["merchantName"]
        mAccount = r["merchantAccount"]

    
        print('res:',r)
        
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        
        if not qr is None:
            return {"status_code": 401, "message": "terminal has active QR request"}
        
        q = QRTer(terminalID = payload["terminalID"],merchantAccount = mAccount,dateTime= datetime.now(),currency=payload["currency"],amount=payload["amount"],displayName=payload["displayName"],merchantName=mName,qrStatus="pending")
        

        db.add(q)
        db.commit()
        db.refresh(q)

    # except Exception as e:
    #     message = "exception occurred with creating QR request"
    #     log(0, message)
    #     return {"status_code": 401, "message": message}

        return {"status_code": 201, "message": q}


@router.post("/cancelQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        # token = payload['token']

    
        print('payload:',payload)
        
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}

        db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").update(
            {"qrStatus": "cancelled"})
        r =requests.post(f"http://{currentServer}:8080/transaction", json={ "customerID": "None","displayName":qr.displayName,"accountNo":"None","message":"transaction registered","transactionStatus":"cancelled","transactionID":"None","terminal":qr.terminalID,"amount":qr.amount,"currency":qr.currency})
        db.commit()

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Payment has been cancelled"}

@router.post("/timeOutQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        # token = payload['token']

    
        print('payload:',payload)
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}

        db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").update(
            {"qrStatus": "timed out"})
        r =requests.post(f"http://{currentServer}:8080/transaction", json={ "customerID": "None","displayName":qr.displayName,"accountNo":"None","message":"transaction registered","transactionStatus":"timed out","transactionID":"None","terminal":qr.terminalID,"amount":qr.amount,"currency":qr.currency})
        db.commit()

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Payment Timed Out"}


@router.post("/rejectQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}

        db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").update(
            {"qrStatus": "rejected"})
        r =requests.post(f"http://{currentServer}:8080/transaction", json={ "customerID": "None","displayName":qr.displayName,"accountNo":"None","message":"transaction registered","transactionStatus":"rejected","transactionID":"None","terminal":qr.terminalID,"amount":qr.amount,"currency":qr.currency})
        db.commit()

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Qr request rejected"}

@router.get("/getQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        # token = payload['token']


        print('payload:',payload)
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}
            
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr}#,"customer":cus, "token": token}


@router.get("/getQrTerIdStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        # token = payload['token']

    
        print('payload:',payload)
        qr = db.query(QRTer).filter(QRTer.id == payload["qrID"]).first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this id"}

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr}  # ,"customer":cus, "token": token}


@router.post("/recCancelQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "user has no active QR request"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").update({"qrStatus":"cancelled"})
        db.commit()
         

    except:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "QR request cancelled", "token": token}

@router.post("/timeOutCancelQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "user has no active QR request"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").update({"qrStatus":"timed out"})
        db.commit()
         

    except:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "QR request timed out", "token": token}

@router.post("/senderReadQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        
        qr = db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").update({"qrStatus":"received"})
        db.commit()
        db.refresh(qr)
         
        db.refresh(rec)
        db.refresh(cus)
        
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec, "token": token}

@router.post("/senderRejectQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        qr = db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").update({"qrStatus":"rejected"})
        db.commit()
        db.refresh(qr)
         
        db.refresh(rec)
        db.refresh(cus)
        
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec, "token": token}

@router.get("/getQrStatus")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        qr = db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec, "token": token}

# @router.get("/getQrTerStatus")
# async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
#     try:
#         payload = await request.body()
#         # payload = json.loads(payload)
#         # payload = payload['message']
#         payload = json.loads(payload)
#         token = payload['token']

    
#         print('payload:',payload)
#         qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"]).first()
#         if qr is None:
#             return {"status_code": 401, "message": "no QR request active by this user"}
        
#     except:
#         message = "exception occurred with getting QR request"
#         log(0, message)
#         return {"status_code": 401, "message": message}

#     return {"status_code": 201, "message": qr}


@router.get("/getQrIdStatus")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        qr = db.query(QR).filter(QR.id == payload["qrID"]).first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this ID"}
        elif not (qr.customerID == payload["id"] or qr.customerID == payload["recId"]) :
            return {"status_code": 401, "message": "this QR is not issued by this user"}
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec, "token": token}


@router.post("/checkPin")
async def checkPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}

        pin = cus.pin

        if pin == payload["pin"]:
            return {"status_code": 201, "message": "Pin Has been entered Successfully", "token": token}

        return {"status_code": 401, "message": "Pin Incorrect", "token": token}
    except:
        message = "exception occurred with checking pin"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/balance")
async def getBal(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        accts = db.query(Account).filter(Account.customerID == payload["id"])
        if accts.first() is None:
            return {"status_code": 400, "message": "customer has no accounts"}

        total_bal = 0
        for i in accts:
            total_bal += i.balance

        return {"status_code": 200, "balance": total_bal, "token": token}
    except:
        message = "exception occurred with checking balance"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/acctBalance")
async def getBal(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        accts = db.query(Account).filter(Account.accountNumber == payload["accountNumber"]).first()
        if accts is None:
            return {"status_code": 400, "message": "account doesn't exist"}

        return {"status_code": 200, "balance": accts.balance, "token": token}
    except:
        message = "exception occurred with checking balance"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/getTransactions")
async def gettrans(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']
        if not 'number' in payload:
            payload["number"] = 20

    
        print('payload:',payload)
        acct = db.query(Account).filter(Account.accountNumber == payload["accountNumber"]).first()
        if acct is None:
            return {"status_code": 400, "message": "account doesn't exist"}
        s = []
        r = []
        acc = acct.accountNumber
        print(acc)
        outg = db.query(Transaction).filter(Transaction.fromAccountNo == acc).all()
        print(outg)
        inc = db.query(Transaction).filter(Transaction.toAccountNo == acc).all()
        for i in outg:
            s.append(i.id + 1)
        for i in inc:
            r.append(i.id - 1)
        s.sort(reverse=True)
        r.sort(reverse=True)
        tr = []
        counter = payload["number"]
        print(s)
        print(r)
        for i in s:
            tran = db.query(Transaction).filter(Transaction.id == i).first()
            tran.fromAccountNo = "from"
            if tran.toAccountNo == "10-00000005-001-00":
                tran.toAccountNo = "fees"
                tran.description = "fees"
            elif tran.toAccountNo == "10-00000003-001-00":
                tran.toAccountNo = "external"
            else:
                tran.description = "Wallet Transfer"
            tr.append(tran)
            if len(tr) == counter/2:
                break
            lenn = len(tr)
        for i in r:
            
            tran = db.query(Transaction).filter(Transaction.id == i).first()
            tran.toAccountNo = "to"
            if tran.fromAccountNo == "10-00000003-001-00":
                tran.fromAccountNo = "external"
            else:
                tran.description = "Wallet Transfer"
            tr.append(tran)
            if len(tr) - lenn == counter/2:
                break
        # tr.reverse()
        

        return {"status_code": 200, "message": tr, "token": token,"length":len(tr)}
    except:
        message = "exception occurred with checking transactions"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/addAcc")
async def addAcct(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        if payload["balance"] < 1:
            return {"status_code": 401, "message": "balance can't be negative"}

        cur = db.query(Currency).filter(
            Currency.country == payload["country"] , Currency.currencyName == payload["currency"]).first()
        if cur is None:
            return {"status_code": 401, "message": "currency doesn't exist in currency table"}
        currency_code = cur.code

        accounts = db.query(Account).filter(Account.customerID == payload["id"]).all()
        subAccount = f"{int(len(accounts) + 1):03}"

        start_position = 12

        newAccountNumber = accounts[0].accountNumber[:start_position] + subAccount + "-" + currency_code
        # same procsess for different currencies

        acco = addAccnt(payload["id"], newAccountNumber, payload["accountType"], payload["balance"], "active", False,
                        db, payload["country"], payload["currency"], payload["friendlyName"],"IEOLW"+newAccountNumber,"IEOLW","xyz 123","One Link Wallet","Dublin, Ireland")
        if not acco["status_code"] == 201:
            return acco
        a = acco["message"]
        n = Notification(customerID=a.customerID, dateTime=datetime.now(), notificationStatus="active",
                         notificationText="Account Has Been Added to Your Profile",notificationType="active",action=f"http://{currentServer}:4000/removeNotification")
        db.add(n)
        db.commit()
        db.refresh(n)
        db.refresh(a)

        return {"status_code": 200, "message": "Account Successfully Created","account":a}
    except:
        message = "exception occurred with adding account"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/kycLevel")
async def getKyc(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        return {"status_code": 200, "message": cus.customerStatus, "token": token}
    except:
        message = "exception occurred with checking kyc"
        log(0, message)
        return {"status_code": 401, "message": message}

@router.post("/removeNotification")
async def remNot(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        db.query(Notification).filter(Notification.id == payload["notifID"]).update({"notificationStatus":"inactive"})
        
        return {"status_code": 200, "message": "notification inactivated", "token": token}
    except:
        message = "exception occurred with checking notifications"
        log(0, message)
        return {"status_code": 401, "message": message}

    

@router.post("/account")
async def getAccount(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        accounts = db.query(Account).filter(Account.customerID == payload["id"]).all()
        user = db.query(Customer).filter(Customer.id == payload["id"]).first()

        return {"status_code": 200, "token": token, "message": accounts,"status":user.customerStatus}
    except:
        message = "exception occurred with checking accounts"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/getNotification")
async def getNotifications(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        notifications = db.query(Notification).filter(Notification.customerID == payload["id"], Notification.notificationStatus == "active").all()
        notifications.reverse()
        return {"status_code": 200, "message": notifications, "token": token}
    except:
        message = "exception occurred with checking notifications"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/sendVerEmail")
async def sendVerEmail(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.email == payload["email"]).first()
        cus.emailCode = send_template_email(cus.email, 1, cus)

        db.query(EmailCode).filter(EmailCode.customerID == cus.id).update({"result": "expired"})
        db.commit()
        db.query(Customer).filter(Customer.id == cus.id).update({"emailCode": cus.emailCode})

        ec = EmailCode(customerID=cus.id, dateTime=datetime.now(), code=cus.emailCode, email=cus.email,
                       expiration=datetime.now() + timedelta(minutes=5), result="pending")

        db.add(ec)
        db.commit()
        db.refresh(ec)
    except:
        message = "exception occurred with retrieving email"
        log(0, message)
        return {"status_code": 401, "message": message}

@router.post("/resendVer")
async def sendVerEmail(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        cus.emailCode = send_template_email(cus.email, 1, cus)
        

        db.query(EmailCode).filter(EmailCode.customerID == cus.id).update({"result": "expired"})
        db.commit()
        db.query(Customer).filter(Customer.id == cus.id).update({"emailCode": cus.emailCode})

        ec = EmailCode(customerID=cus.id, dateTime=datetime.now(), code=cus.emailCode, email=cus.email,
                       expiration=datetime.now() + timedelta(minutes=codeValidMinutes), result="pending")

        db.add(ec)
        db.commit()
        db.refresh(ec)
    except:
        message = "exception occurred with retrieving email"
        log(0, message)
        return {"status_code": 401, "message": message}
    return {"status_code": 200, "message": "Verification Email Sent", "token": token}

@router.post("/resendUpdateVer")
async def sendVerEmail(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        
        ec1 = db.query(EmailCode).filter(EmailCode.customerID == payload["id"] , EmailCode.result=="pending").first()
        
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        cus.emailCode = send_template_email(ec1.email, 3, cus)

        db.query(EmailCode).filter(EmailCode.customerID == cus.id).update({"result": "expired"})
        db.query(Customer).filter(Customer.id == cus.id).update({"emailCode": cus.emailCode})

        ec = EmailCode(customerID=cus.id, dateTime=datetime.now(), code=cus.emailCode, email=ec1.email,
                       expiration=datetime.now() + timedelta(minutes=codeValidMinutes), result="pending")

        db.add(ec)
        db.commit()
        db.refresh(ec)
    except:
        message = "exception occurred with retrieving email"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 200, "message": "Email Sent", "token": token}
    

@router.get("/email/{user_id}")
async def verEmail(user_id, request: Request, db: Session = Depends(get_db)):
    try:
        code = decode(user_id)
        ec = db.query(EmailCode).filter(EmailCode.code == code).first()
        id = ec.customerID
        cus = db.query(Customer).filter(Customer.id == id).first()

        if datetime.now() > datetime.strptime(ec.expiration, '%Y-%m-%d %H:%M:%S.%f'):
            db.query(EmailCode).filter(EmailCode.customerID == cus.id).update({"result": "expired"})
            return {"status_code": 401, "message": "this code has expired"}
        elif ec.result == "expired":
            return {"status_code": 401, "message": "this code has expired"}

        if cus is None:
            return {"status_code": 401, "message": "an error occured, please try again"}
        elif cus.emailCode == "-1":
            return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Link Invalid</title>
                </head>
                <body>
                    <h1>Link Invalid</h1>
                    <p>The link you provided is invalid.</p>
                </body>
                </html>
                """)

        e = Email(emailAddress=cus.email, emailStatus="active", customerID=cus.id, dateTime=datetime.now())

        db.query(Customer).filter(Customer.email == cus.email).update(
            {"customerStatus": "first level", "emailCode": "-1"})
        db.query(EmailCode).filter(EmailCode.code == code).update({"result": "confirmed"})

        db.add(e)

        send_template_email(e.emailAddress, 0, cus)
        n = Notification(customerID=cus.id, dateTime=datetime.now(), notificationStatus="active",
                         notificationText="Your email has been verified",notificationType="email verified")
        n2 = updateNotif(db,cus.id,"outdated","email registeration")
        db.add(n)
        db.commit()
        db.refresh(n)
        db.refresh(e)
        return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Verification complete</title>
                </head>
                <body>
                    <h1>verification Complete</h1>
                    <p>you have been verified.</p>
                </body>
                </html>
                """)

    except:
        message = "exception occurred with retrieving email"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.get("/updateEmail/{user_id}")
async def updateEmail(user_id, request: Request, db: Session = Depends(get_db)):
    try:
        code = decode(user_id)
        ec = db.query(EmailCode).filter(EmailCode.code == code).first()
        id = ec.customerID
        cus = db.query(Customer).filter(Customer.id == id).first()

        if datetime.now() > datetime.strptime(ec.expiration, '%Y-%m-%d %H:%M:%S.%f'):
            db.query(EmailCode).filter(EmailCode.customerID == cus.id).update({"result": "expired"})
            return {"status_code": 401, "message": "this code has expired"}
        elif ec.result == "expired":
            return {"status_code": 401, "message": "this code has expired"}

        if cus is None:
            return {"status_code": 401, "message": "an error occured, please try again"}
        elif cus.emailCode == "-1":
            return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Link Invalid</title>
                </head>
                <body>
                    <h1>Link Invalid</h1>
                    <p>The link you provided is invalid.</p>
                </body>
                </html>
                """)

        e = Email(emailAddress=ec.email, emailStatus="active", customerID=cus.id, dateTime=datetime.now())
        db.query(Email).filter(Email.emailAddress == cus.email).update({"emailStatus": "outdated"})
        db.add(e)

        db.query(Customer).filter(Customer.email == cus.email).update({"email": ec.email, "emailCode": -1})
        db.query(EmailCode).filter(EmailCode.code == code).update({"result": "confirmed"})

        send_template_email(ec.email, 2, cus)
        n = Notification(customerID=cus.id, dateTime=datetime.now(), notificationStatus="active",
                         notificationText="Your email has been updated",notificationType="email updated")
        n2 = updateNotif(db,cus.id,"outdated","email update")
        db.add(n)
        db.commit()
        db.refresh(n)
        db.refresh(e)
        return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Update complete</title>
                </head>
                <body>
                    <h1>Email Update Complete</h1>
                    <p>you have been verified.</p>
                </body>
                </html>
                """)

    except:
        message = "exception occurred with retrieving email"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.post("/updateMobile")
async def sendSms(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()

        if cus is None:
            return "no customer exists with this id"

        n = Mobile(mobileNumber=payload["mobileNumber"], countryCode=payload["countryCode"], numberStatus="active",
                   customerID=cus.id, dateTime=datetime.now())
        db.query(Mobile).filter(Mobile.customerID == payload["id"]).update({"numberStatus": "outdated"})
        db.query(Customer).filter(Customer.id == payload["id"]).update(
            { "smsCode": "-1"})

        db.add(n)
        db.commit()
        db.refresh(n)

    except:
        message = "exception occurred with creating mobile"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "mobile Succefully added"}


@router.get("/test")
async def test(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    client_host = request.client.host  # Client's IP address
    client_port = request.client.port  # Client's port
    user_agent = request.headers.get("user-agent")  # User-Agent header
    referer = request.headers.get("referer")  # Referer header
    content_type = request.headers.get("content-type")  # Content-Type header
    content_length = request.headers.get("content-length")  # Content-Length header
    query_params = dict(request.query_params)  # Query parameters
    cookies = dict(request.cookies)  # Cookies

    return {
        "Client Host": client_host,
        "Client Port": client_port,
        "User Agent": user_agent,
        "Referer": referer,
        "Content Type": content_type,
        "Content Length": content_length,
        "Query Parameters": query_params,
        "Cookies": cookies,
        "hostIP":currentServer,
        "hostPort":currentPort
    }


@router.post("/getUserDetails")
async def getBal(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        user = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if user is None:
            return {"status_code": 400, "message": "no user with such an ID"}
        mob = db.query(Mobile).filter(Mobile.customerID == user.id, Mobile.numberStatus == "active").first()
        kyc = db.query(KYC).filter(KYC.customerID == user.id, KYC.kycStatus == "active").first()
        kyc2 = db.query(KYC2).filter(KYC2.customerID == user.id, KYC2.kycStatus == "active").first()
        
        return {"status_code": 200, "data": user, "token": token,"mobile":mob,"kyc":kyc,"kyc2":kyc2}
    except:
        message = "exception occurred with retrieving details"
        log(0, message)
        return {"status_code": 401, "message": message}


@router.get("/getKYC2")
async def getkyc2(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        opts = db.query(Options).filter(Options.table == "KYC2").all()
        displayOptions = {}
        for i in opts:
            displayOptions[i.name] = read_lines_in_range("employmentOptions/"+i.name+".txt",i.start,i.end)
        return {"status_code": 200, "data": displayOptions}
    except:
        message = "exception occurred with retrieving opts"
        log(0, message)
        return {"status_code": 401, "message": message}
    



@router.post("/initOpts")
async def ops(request: Request, db: Session = Depends(get_db)):
    # try:
    opts = db.query(Options).filter(Options.table == "KYC2").all()
    if len(opts) == 0:
        o1 = Options(name="employment",table="KYC2",start=1,end=7)
        o2 = Options(name="sourceOfIncome",table="KYC2",start=1,end=4)
        o3 = Options(name="profession",table="KYC2",start=1,end=13)
        o4 = Options(name="incomeRange",table="KYC2",start=1,end=4)

        db.add(o1)
        db.add(o2)
        db.add(o3)
        db.add(o4)
        db.commit()
        db.refresh(opts)
        
        return {"status_code": 200,"message":"opts intialized","opts":opts}
    return {"status_code": 400,"message":"opts already exist","opts":opts}
    # except:
    #     message = "exception occurred with retrieving opts"
    #     log(0, message)
    #     return {"status_code": 401, "message": message}

@router.post("/loginSms")
async def signInSms(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if not cus:
            return {"status_code": 404, "message": "no user exists with this id"}
        # mob = db.query(Mobile).filter(Mobile.customerID ==cus.id).first()
        sms = addSMS(cus.id, payload["mobile"], payload["countryCode"], db)
        db.commit()
        if sms["status_code"] == 201:
            return sms["message"]
        else:
            return sms
    except:
        message = "exception occurred with retrieving customer"
        log(0, message)
        return {"status_code": 401, "message": message}

@router.post("/loginCheck")
async def signIn(request: Request, payload2: dict = Body(...), db: Session = Depends(get_db)):
    # try:
        payload = await request.body()
        payload = json.loads(payload)
        # payload = payload['message']
        # payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        em = payload["email"]
        
        pa = payload["password"]
        user = db.query(Customer).filter(Customer.email == em).first()

        if not user:
            return {"status_code": 403, "message": "wrong email or password!"}
        print('a')
        password = db.query(Password).filter(Password.customerID == str(user.id) , Password.passwordStatus == "active").first()
        hashed_password = pa.encode('utf-8')
        print("b")
        if not Hasher.verify_password(hashed_password, password.passwordHash):
            return {"status_code": 404, "message": "wrong email or password!!", "orig": hashed_password,
                    "other": password}
        otp = "1111"
        print('c')
        user.smsCode = otp
        user.smsValid = datetime.now() + timedelta(days=365)
        db.query(Customer).filter(Customer.email == em).update({"smsCode":otp,"smsValid":user.smsValid})
        print('d')
        db.commit()
        print('e')
        smsList.append({"phone_number": user.countryCode+user.phoneNumber, "message": "your otp is:"+otp})
        print('f')
        print("login success")
        return {"status_code":200,"message":"email and password correct","otp":otp,"customerID":user.id}
    # except:
    #     message = "exception occurred with checking credentials"
    #     log(0, message)
    #     return {"status_code": 401, "message": message}

class SMSResponse(BaseModel):
    phone_number: str
    message: str

class SMSRequest(BaseModel):
    phone_number: str
    message: str

@router.post("/postsms")
def post_sms(sms: SMSRequest):
    try:
        smsList.append({"phone_number": sms.phone_number, "message": sms.message})
        print("Post message", sms.phone_number, sms.message)
        return {"status": "SMS received"}
    except:
        message = "exception occurred with sms"
        log(0, message)
        return {"status_code": 401, "message": message}
    
@router.post("/getsms", response_model=SMSResponse)
def get_sms():
    try:
        if not smsList:
            raise HTTPException(status_code=404, detail="No SMS found")

        latest_sms = smsList.pop(0)  # Get and remove the first (oldest) SMS
        print("Sent sms", latest_sms)
        return latest_sms
    except:
        message = "exception occurred with retrieving customer"
        log(0, message)
        return {"status_code": 401, "message": message}
    
@router.post("/login")
async def signIn(request: Request, payload2: dict = Body(...), db: Session = Depends(get_db)):
    # try:
        payload = await request.body()
        payload = json.loads(payload)
        # payload = payload['message']
        # payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()

        if not cus.smsCode == payload['code']:
            print(cus.smsCode)
            return {"status_code": 404, "message": "wrong code"}
        elif datetime.now() > datetime.strptime(cus.smsValid, '%Y-%m-%d %H:%M:%S.%f'):
            return {"status_code": 404, "message": "code timed- out"}


        
        # tokens[token]['id'] = cus.id
        


        account = db.query(Account).filter(Account.customerID == str(cus.id), Account.primaryAccount == "1").first()
        bank = db.query(Bank).filter(Bank.accountNumber == account.accountNumber).first()
        bankb = db.query(BankBusiness).filter(BankBusiness.accountNumber == account.accountNumber).first()
        return {"status_code":200,"user":cus,"token":token,"account":account,"bank":bank,"bankBusiness":bankb}

        

    # except:
    #      message = "exception occurred with logining in"
    #      log(0,message)
    #      return {"status_code":401,"message":message}
    
@router.post("/getAddress")
async def getAdd(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        return getAddress(payload["id"],db)
    except:
        message = "exception occurred with retrieving Address"
        log(0, message)
        return {"status_code": 401, "message": message}



def getAddress(id, db: Session = Depends(get_db())):
    try:
        a = db.query(Address).filter(Address.customerID == id , Address.addressStatus == "active").first()
        k = db.query(KYC).filter(KYC.customerID == id , KYC.kycStatus == "active").first()

        if a is None or k is None:
            return {"status_code": 401, "message": "customer has not provided address"}

        return  {"status_code": 201, "message": {a,k}}
    except:
        message = "exception occurred with retrieving address"
        log(0, message)
        return {"status_code": 401, "message": message}       

def addSMS(id, mobile, countrycode, db: Session = Depends(get_db())):
    try:
        confrimation_code = random.randint(100000, 999999)
        confrimation_code = 1111 ###########edit

        message = "your confirmation code is: " + str(confrimation_code)

        cus = db.query(Customer).filter(Customer.id == id).first()
        if (cus is None):
            return False


        nowP5 = datetime.now() + timedelta(minutes=5)
        nowP5 = datetime.now() + timedelta(days=365) ####edit
        cus = db.query(Customer).filter(Customer.id == id).update({"smsCode": confrimation_code, "smsValid": nowP5})

        s = Sms(customerID=id, dateTime=datetime.now(), message=confrimation_code, mobileNumber=mobile,
                countryCode=countrycode, priority="1", result="pending")

        db.add(s)

        return {"status_code": 201, "message": str(confrimation_code)}
    except:
        message = "exception occurred with retrieving token"
        log(0, message)
        return {"status_code": 401, "message": message}


def addPassword(id, password, db: Session = Depends(get_db())):
    try:
        cus = db.query(Customer).filter(Customer.id == id).first()
        passwordO = db.query(Password).filter(Password.customerID == id, passwordStatus="active").update(
            {"passwordStatus": "outdated"})

        return {"status_code": 201, "message": newPassword(password)}
    except:
        message = "exception occurred with retrieving token"
        log(0, message)
        return {"status_code": 401, "message": message}


def newPassword(password):
    if len(password) > passwordMax or len(password) < passwordMin:
        return False

    salt = bcrypt.gensalt()
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_password = Hasher.get_password_hash(password)
    return hashed_password


def addAccnt(id, acctNo, acctType, bal, status, primary: bool, db, country, currency, friendlyName,iBan,bic,swift,bankName,bankAddress):
    try:
        a = Account(customerID=id, accountNumber=acctNo, accountType=acctType, balance=bal, dateTime=datetime.now(),
                    accountStatus=status, primaryAccount=primary, currency=currency, country=country,
                    friendlyName=friendlyName,iban =iBan,bic = bic,swift = swift,bankName = bankName,bankAddress=bankAddress )
        db.add(a)
        return {"status_code": 201, "message": a}
    except:
        message = "exception occurred with retrieving token"
        log(0, message)
        return {"status_code": 401, "message": message}


def hashPassword(inpass):
    password = "MySecurePassword123"

    # Hash a password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Verify a password
    user_input_password = "WrongPassword123"
    if bcrypt.checkpw(user_input_password.encode('utf-8'), hashed_password):
        print("Password is correct.")
    else:
        print("Password is incorrect.")
    return password


def send_template_email(receiver_email, template_number, customer):
    # 0 welcome, 1 registration confirmation, 2 account updated, 3 password changed, 4 transaction complete
    sender_email = 'thahuntar@gmail.com'
    sender_password = 'beez xclv ypet nkts'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    confrimation_code = random.randint(100000, 999999)
    try:
        # Create an SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Log in to your email account
        server.login(sender_email, sender_password)

        # Define email templates
        htmlname = "emailTemplates/temp" + str(template_number) + ".html"
        with open(htmlname, "r") as template_file:
            email_template = template_file.read()

        email_content = email_template.replace("[Recipient's Name]", customer.firstName)
        if template_number == 1:
            email_content = email_content.replace("[Confirmation Link]",
                                                  f"http://{currentServer}:4000/email/" + encode(
                                                      str(confrimation_code)))
        if template_number == 3:
            email_content = email_content.replace("[Confirmation Link]",
                                                  f"http://{currentServer}:4000/updateEmail/" + encode(
                                                      str(confrimation_code)))

        subject_templates = ["Welcome to Our Platform", "Registration Confirmation", "Account Updated",
                             "email update confirmations", "Email Update Confirmation"]
        # Create a message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject_templates[template_number]

        # Attach the message body
        message.attach(MIMEText(email_content, 'html'))

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

        # Close the connection
        server.quit()

        print(f"Email sent to {receiver_email} successfully.")
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {str(e)}")

    return str(confrimation_code)


def is_18_or_older(birthdate):
    # Get the current date
    current_date = datetime.now().date()

    # Calculate the age by subtracting the birthdate from the current date
    age = current_date.year - birthdate.year - (
                (current_date.month, current_date.day) < (birthdate.month, birthdate.day))

    # Check if the age is greater than or equal to 18
    return age >= 18


def encode(num):
    num = list(num)
    code = ["1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    free = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    pointer = 0
    for i in num:
        code, free, pointer = move(code, free, int(i), pointer)

    output_code = ""
    for j in range(len(code)):
        if free[j] == "0":
            code[j] = str(randrange(10))
        output_code += code[j]
    return str(output_code)


def move(code, free, steps, pointer):
    code[pointer] = str(steps)
    free[pointer] = "1"
    while steps >= 0:
        pointer = (pointer + 1) % 16
        if free[pointer] == "0":
            steps -= 1

    return code, free, pointer


def readMove(free, steps, pointer):
    free[pointer] = "1"
    while steps >= 0:
        pointer = (pointer + 1) % 16
        if free[pointer] == "0":
            steps -= 1
    return free, pointer


def decode(url):
    free = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    code = ""
    numbers = list(url)
    pointer = 0
    for i in range(6):
        code += numbers[pointer]
        free, pointer = readMove(free, int(numbers[pointer]), pointer)
    return code


def generateToken(id):
    time = datetime.now() + timedelta(minutes=15)
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    minute = time.minute
    zeroes = ["", "", "", ""]  # month,day,hour,minute
    if minute < 10:
        zeroes[3] = "0"
    if hour < 10:
        zeroes[2] = "0"
    if day < 10:
        zeroes[1] = "0"
    if month < 10:
        zeroes[0] = "0"
    intial = zeroes[3] + str(minute) + zeroes[0] + str(month) + zeroes[2] + str(hour) + str(year) + zeroes[1] + str(
        day) + str(id)
    final = ""
    for i in intial:
        final = final + str(9 - int(i))
    return final


def checkToken(id, token):
    revId = token[12:]
    checker = "9999999999999"
    curCheck = checker[0:len(revId)]
    if not int(id) + int(revId) == int(curCheck):
        return False
    values = ""
    for i in token:
        values = values + str(9 - int(i))
    expiration = datetime(year=int(values[6:10]), month=int(values[2:4]), day=int(values[10:12]), hour=int(values[4:6]),
                          minute=int(values[0:2]))
    if datetime.now() > expiration:
        return False
    return True


def updateToken(id, db):
    token = db.query(Token).filter(Token.customerID == id, Token.status == "active").first()
    if token == None:
        return False
    db.query(Token).filter(Token.customerID == id, Token.status == "active").update(
        {"token": generateToken(id), "expiration": datetime.now() + timedelta(minutes=tokenValidMins)})
    db.commit()
    token = db.query(Token).filter(Token.customerID == id, Token.status == "active").first()

    return token


def generate_bank_account(db,account_type="01", sub_account="001", currency_code="01"):
    # Load the last generated account number from a file, or use defaults if the file doesn't exist.
    numberOfTrials = 20
    timeoutTime = 1
    while numberOfTrials>0:
        entry = db.query(LastAccount).filter(LastAccount.status == "active").first()
        if entry is None:
            return {"status_code": 401, "message": "no last account number entry in DB"}
        print(entry.busy)
        print(numberOfTrials)
        if entry.busy:
            asyncio.sleep(timeoutTime)
            if numberOfTrials == 1:
                return {"status_code": 401, "message": "timed out creating account"}
            numberOfTrials -=1

        else:
            last_account_number = entry.lastNumber
            db.query(LastAccount).filter(LastAccount.id == entry.id).update({"busy":True})
            db.commit()

            account_type_str = f"{int(account_type):02}"
            sub_account_str = f"{int(sub_account):03}"
            currency_code_str = f"{int(currency_code):02}"

# Increment the account number and save it back to the file
            last_account_number += 1


# Construct the bank account number
            account_number_str = f"{last_account_number+100:08}"
            bank_account = f"{account_type_str}-{account_number_str}-{sub_account_str}-{currency_code_str}"

            db.query(LastAccount).filter(LastAccount.id == entry.id).update({"busy":False,"lastAccountNumber":bank_account,"lastNumber":last_account_number})
            db.commit()

            return {"status_code": 201, "message":bank_account}

def createNotif(db,customerID,notificationText,notificationType,action):
    n = Notification(customerID=customerID,dateTime=datetime.now(),notificationText=notificationText,notificationType=notificationType,notificationStatus="active",action=action)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n

def updateNotif(db,cusID,notifStatus,notifType):
    db.query(Notification).filter(Notification.customerID==cusID).update({"notificationStatus":notifStatus})
    db.commit()

def log(logFile, message):
    # error,transaction,login
    if logFile == 0:
        fileName = "logs/errors.txt"
    if logFile == 1:
        fileName = "logs/transactions.txt"
    if logFile == 2:
        fileName = "logs/login.txt"

    file_object = open(fileName, 'a')
    file_object.write(message + '\n')
    file_object.close()
    return True

@router.get("/test2")
async def test(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    n = createNotif(db,payload["customerID"],payload["text"],payload["type"],"resend")
    return n

@router.get("/test3")
async def test(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    n = updateNotif(db,payload["id"],payload["status"])
    return n

def read_lines_in_range(file_path, start_line, end_line):
    result = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        #return lines

        start_index = start_line - 1
        end_index = end_line

        if 0 <= start_index < len(lines) and 0 <= end_index <= len(lines):
            result = [line.strip() for line in lines[start_index:end_index]]

    return result
