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
from db.models.lastAccount import LastAccount
from db.models.transactionType import TransactionType


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
@router.post("/testInit")
async def intiAccts(request: Request=None,response: Response=None,db: Session = Depends(get_db)):
    
    
    return {"status_code": 201, "message": "transaction types added"}

@router.post("/initAccts")
async def intiAccts(request: Request=None,response: Response=None,db: Session = Depends(get_db)):
        print("init")
        adm = db.query(Customer).filter(Customer.customerStatus == "admin").first()
        addFee("M001","ACM","Account Maintenance","Fees for maintaining an active eWallet account","Monthly/Annual account maintenance fee","AMF001","000",10,2,5,1,db)
        addFee("M001", "TRN", "Transaction Fees", "Fees associated with various types of transactions", "Fee for sending money to other users or external accounts", "TF001", "000", 50, 0.5, 1.5, 1, db)

        addFee("M001", "TRN", "Transaction Fees", "Fees associated with various types of transactions", "Fee for receiving money from other users or external accounts", "TF002", "000", 30, 0.3, 0.5, 1, db)

        addFee("M001", "TRN", "Transaction Fees", "Fees associated with various types of transactions", "Fee for merchant payments", "TF003","000", 100, 1, 2.5, 1, db)

        addFee("M001", "TRN", "Transaction Fees", "Fees associated with various types of transactions", "Fee for bill payments", "TF004", "000", 20, 1, 3, 1, db)

        addFee("M001", "TRN", "Transaction Fees", "Fees associated with various types of transactions", "Fee for currency conversion", "TF005", "000", 50, 1, 2.5, 1, db)

        addFee("M001", "DEP", "Deposit and Withdrawal Fees", "Fees for depositing or withdrawing money", "Fee for bank transfers to/from eWallet", "DWF001", "000", 25, 0.5, 1.3, 1, db)

        addFee("M001", "DEP", "Deposit and Withdrawal Fees", "Fees for depositing or withdrawing money", "Fee for adding money using a credit/debit card", "DWF002", "000", 30, 1, 2.4, 1, db)

        addFee("M001", "DEP", "Deposit and Withdrawal Fees", "Fees for depositing or withdrawing money", "Fee for ATM withdrawals using eWallet card", "DWF003", "000", 5, 1, 1.2, 1, db)

        addFee("M001", "SRV", "Service Fees", "Additional service-related fees", "Fee for inactive accounts", "SF001", "000", 20, 1, 0, 1, db)

        addFee("M001", "SRV", "Service Fees", "Additional service-related fees", "Fee for account closure", "SF002", "000", 10, 2, 0, 1, db)

        addFee("M001", "SRV", "Service Fees", "Additional service-related fees", "Fee for chargebacks", "SF003", "000", 25, 5, 1.5, 1, db)

        addFee("M001", "PRM", "Premium Services Fees", "Fees for premium eWallet services", "Subscription fee for premium services", "PSF001", "000", 100, 10, 0, 1, db)

        addFee("M001", "PRM", "Premium Services Fees", "Fees for premium eWallet services", "Fee for issuing and using virtual card", "PSF002", "000", 50, 5, 0, 1, db)

        addFee("M001", "INT", "International Transaction Fees", "Fees for international transactions", "Fee for cross-border transactions", "ITF001", "000", 40, 2, 1.4, 1, db)

        addFee("M001", "INT", "International Transaction Fees", "Fees for international transactions", "Fee for international money transfers", "ITF002", "000", 60, 5, 2.6, 1, db)

        addFee("M001", "ADM", "Administrative Fees", "Fees for administrative services", "Fee for providing paper account statements", "AF001", "000", 15, 1, 0, 1, db)

        addFee("M001", "ADM", "Administrative Fees", "Fees for administrative services", "Fee for reissuing lost or expired cards", "AF002", "000", 20, 2, 0, 1, db)

        addFee("M001", "MRC", "Merchant Fees","Fees merchant transaction","Fee for merchant transaction","MR002","000",0,0,1.5,0.1,db)

        cur = Currency(country="USA",currencyName="USD",code="01",status="active")
        db.query(Currency).filter(Currency.country=="USA",Currency.currencyName=="USD",Currency.code=="01").update({"status":"expired"})
        db.add(cur)
        l = LastAccount(lastNumber = 0,lastAccountNumber = None,busy = False,status = "active")
        db.query(LastAccount).update({"status":"expired"})
        db.add(l)
        if not adm is None:
            db.commit()
            return {"status_code": 201,"message":"wallet initiated"}
        admin = Customer(firstName="OLW",lastName="",email="",birthdate="",customerStatus="admin",customerNumber = '00000001')
        db.add(admin)
        
        OLWBank = db.query(Account).filter(Account.accountNumber == "1").first()
        if OLWBank is None:
            olw = Account(customerID="1",accountNumber="10-00000003-001-00",accountType="OLW",balance=10000,dateTime=datetime.now(),accountStatus="Admin",primaryAccount=1,currency="UNI",country="UNI",friendlyName="bank",iban = "IEOLW10-00000003-001-00",bic = "IEOLW",swift = "SWIFT/PIC xyz 123",bankName = "One Link Wallet",bankAddress = "Dublin, Ireland")
            db.add(olw)

        OLWAudit = db.query(Account).filter(Account.accountNumber == "2").first()
        if OLWBank is None:
            olw = Account(customerID="1",accountNumber="10-00000001-001-00",accountType="OLW",balance=0,dateTime=datetime.now(),accountStatus="Admin",primaryAccount=1,currency="UNI",country="UNI",friendlyName="audit",iban = "IEOLW10-00000001-001-00",bic = "IEOLW",swift = "SWIFT/PIC xyz 123",bankName = "One Link Wallet",bankAddress = "Dublin, Ireland")
            db.add(olw)
            
        OLWFees = db.query(Account).filter(Account.accountNumber == "3").first()
        if OLWFees is None:
            olw = Account(customerID="1",accountNumber="10-00000005-001-00",accountType="OLW",balance=10000,dateTime=datetime.now(),accountStatus="Admin",primaryAccount=1,currency="UNI",country="UNI",friendlyName="fees",iban = "IEOLW10-00000005-001-00",bic = "IEOLW",swift = "SWIFT/PIC xyz 123",bankName = "One Link Wallet",bankAddress = "Dublin, Ireland")
            db.add(olw)
        
        db.commit()
        t1 = addTranType(db,tCode="GEN",tName = "general")
        t2 = addTranType(db,tCode="WAL",tName = "wallet")
        t3 = addTranType(db,tCode="BAN",tName= "bank")
        t4 = addTranType(db,tCode="MER",tName= "merchant")
        t5 = addTranType(db,tCode="WAQ",tName = "wallet qr")
        t6 = addTranType(db,tCode="CHR",tName = "charge")

        if not t1["status_code"] == 201:
            return t1
        if not t2["status_code"] == 201:
            return t2
        if not t3["status_code"] == 201:
            return t3
        if not t4["status_code"] == 201:
            return t4
        if not t5["status_code"] == 201:
            return t5
        if not t6["status_code"] == 201:
            return t6
        return {"status_code": 201, "message": "wallet and fees added"}


@router.post("/transaction")
async def tansaction1(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        # try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            idn = generateTranIdentifier(db,"WAL")
            if not idn["status_code"]==201:
                    return idn
            
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-00").first()
            
            emailPhone = payload["phoneORemail"]
            email = db.query(Email).filter(Email.emailAddress==emailPhone).first()
            mobile=db.query(Mobile).filter(Mobile.mobileNumber == emailPhone).first()
            
            
            if (email is None) and (mobile is None):
                return{"status_code":404,"message":"Email/mobile number does not exist. Please provide a valid email or mobile number"}
            elif email is None:
                customerID = mobile.customerID
            elif mobile is None:
                customerID = email.customerID
            
            cus = db.query(Customer).filter(Customer.id==customerID).first()
            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()
            acc = db.query(Account).filter(Account.customerID ==customerID , Account.primaryAccount).first()
            
            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"Pin incorrect!!"}
            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if payload["amount"]+payload["fees"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}
            
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            
            trans = transactionOperation(idn["message"],payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db)
            if not trans["status_code"]==201:
                return trans
                        
            if payload["fees"]>0:
                trans2 = transactionOperation(idn["message"],payload["fromAccount"],"10-00000005-001-00",payload["fees"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
            log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
            db.commit()
            db.refresh(cus)
            tra1 = db.query(Transaction).filter(Transaction.id == trans["t1"]).first()
            return {"status_code": 201, "customer": cus,"token":token,"message":"transaction registered","transactions":tra1}

            
        # except:
        #     message = "exception occurred with creating transaction"
        #     log(0,message)
        #     return {"status_code":401,"message":message}
        
@router.post("/transactionQr")
async def tansaction1(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            idn = generateTranIdentifier(db,"WAQ")
            if not idn["status_code"]==201:
                    return idn
                
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-00").first()
            
            
            cus = db.query(Customer).filter(Customer.id==payload["recID"]).first()
            if cus is None:
                return {"status_code": 401,"message":"receiving customer doesn't exist"}
            
            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()
            
            acc = db.query(Account).filter(Account.customerID ==payload["recID"]  ,Account.primaryAccount).first()
            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"Pin incorrect"}
            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if payload["amount"]+payload["fees"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}
            
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            trans = transactionOperation(idn["message"],payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db)
            if not trans["status_code"]==201:
                return trans
            q = db.query(QR).filter(QR.id == payload["qrID"]).first()
            
            if q is None:
                return{"status_code":404,"message":"no qr code exists with this ID"}
            elif q.qrStatus == "completed":
                return{"status_code":404,"message":"transaction already complete"}
            
            
            
            db.query(QR).filter(QR.id == payload["qrID"]).update({"transactionID":trans["t1"]})

            db.query(QR).filter(QR.id == payload["qrID"]).update({"qrStatus":"completed"})
            if payload["fees"]>0:
                trans2 = transactionOperation(idn["message"],payload["fromAccount"],"10-00000005-001-00",payload["fees"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
            
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
        tra = db.query(Transaction).filter(Transaction.id == trans["t1"]).first()
        db.refresh(cus)
        return {"status_code": 201, "customer": cus,"token":token,"message":"transaction registered","transaction":tra}

@router.post("/transactionMerchant")
async def tansaction1(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            idn = generateTranIdentifier(db,"MER")
            if not idn["status_code"]==201:
                    return idn
            
            qrt = db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "pending").first()
            if qrt is None:
                return{"status_code":403,"message":"terminal qr code is not pending here"}
            db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "pending").update({"qrStatus":"processing"})
            db.commit()
        
            
            
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()


            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()

            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"Pin incorrect"}

            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if sendAcc is None:
                return {"status_code": 401,"message":"return account doesn't exist"}
            if payload["amount"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}

            if OLWBank is None:
                return{"status_code":404,"message":"please make sure olw bank account are intialized"}
            qrt = db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "processing").first()
            if qrt is None:
                return{"status_code":403,"message":"terminal qr code is not pending here"}
            trans = transactionOperation(idn["message"],payload["fromAccount"],qrt.terminalID,qrt.amount,payload["fromCurrency"],payload["toCurrency"],db,displayName="merchant:"+qrt.merchantName,merchantAccount = qrt.merchantAccount)
            if not trans["status_code"]==201:
                return trans
            r =requests.get("http://192.223.11.185:8080/terminal", json={'id': payload["terminal"]})
            print(r)
            r = json.loads(r.content)
            print("response:",r)

            fee = calcFee(db,payload["amount"],"MR002",r["merchantID"])
            print(fee)
            if fee["status_code"] == 201:
                trans2 = transactionOperation(idn["message"],qrt.merchantAccount,"10-00000005-001-00",fee["fee"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
            else:
                return fee
        

            # q = db.query(QR).filter(QR.id == payload["qrID"]).first()
            
            # if q is None:
            #     return{"status_code":404,"message":"no qr code exists with this ID"}
            # elif q.qrStatus == "completed":
            #     return{"status_code":404,"message":"transaction already complete"}


            
            db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "processing").update({"transactionID":trans["t1"]})

            db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "processing").update({"qrStatus":"completed"})


        except Exception as e:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":e}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],payload["terminal"],payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
        db.refresh(sendAcc)
        db.refresh(sendCus)
        
        tra = db.query(Transaction).filter(Transaction.id == trans["t1"]).first()
        
        r =requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": sendCus.id,"accountNo":sendAcc.accountNumber,"message":"transaction registered","transactionStatus":tra.transactionStatus,"transactionID":tra.id,"terminal":payload["terminal"],"amount":payload["amount"],"currency":payload["toCurrency"]})
        
        
        return {"status_code": 201, "customer": sendCus,"account":sendAcc,"message":"transaction registered","transactions":tra,"token":token,"response":r.json}


@router.post("/transactionOut")
async def tansaction2(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            idn = generateTranIdentifier(db,"BAN")
            if not idn["status_code"]==201:
                    return idn
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-00").first()
            iBan = payload["iBan"]
            
            

            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()
            
            
            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"Pin incorrect"}
            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if sendAcc is None:
                return {"status_code": 401,"message":"sending account doesn't exist"}
            elif sendAcc.customerID == payload["id"]:
                return {"status_code": 401,"message":"sending account doesn't belong to this user"}
            
            if payload["amount"]+payload["fees"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            
            trans = transactionOperation(idn["message"],payload["fromAccount"],iBan,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db)
            if not trans["status_code"]==201:
                return trans
            
            if payload["fees"]>0:
                trans2 = transactionOperation(idn["message"],payload["fromAccount"],"10-00000005-001-00",payload["fees"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],("iBan"+iBan),payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
         
        return {"status_code": 201, "token":token,"message":"transaction registered"}        

def tansaction3(intransID,db: Session = Depends(get_db)):
        try:
            idn = generateTranIdentifier(db,"BAN")
            if not idn["status_code"]==201:
                    return idn
            intrans = db.query(TransactionRequestIncoming).filter(TransactionRequestIncoming.id == intransID).first()
            
            if intrans == None:
                return {"status_code":404,"message":"no such transaction requested"}
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-00").first()
            db.query(TransactionRequestIncoming).filter(TransactionRequestIncoming.id == intransID).update({"transactionStatus":"processed"})
            db.commit()
            
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            feesCode=intrans.feesCode
            amount=intrans.amount
            trans = transactionOperation(idn["message"],intrans.inIBan,intrans.accountNo,intrans.amount,intrans.sendingCurrency,intrans.currency,db)
            
            if not trans["status_code"]==201:
                return trans
            
            feeM = calcFee(db,amount,feesCode)   
            
            if not feeM["status_code"]==201:
                return feeM
            if feeM["fee"]>0:
                trans2 = transactionOperation(idn["message"],intrans.accountNo,"10-00000005-001-00",feeM["fee"],intrans.sendingCurrency,intrans.currency,db)
                
                if not trans2["status_code"]==201:
                    return trans2
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(intrans.inIBan,intrans.accountNo,intrans.amount,intrans.sendingCurrency,intrans.currency))
        return {"status_code": 201,"message":"transaction registered"}

@router.get("/testT")
async def testT(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        return addCharge(db,payload["id"],payload["currency"],payload["amount"],payload["feesService"],payload["feesCurr"],"card")
    except:
        message = "exception occurred with retrieving currencies"
        log(0,message)
        return {"status_code":401,"message":message}
  

@router.post("/bank")
async def createBank(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            
            accountNo=payload["accountNo"]
            bankName=payload["bankName"]
            country=payload["country"]
            currency=payload["currency"]
            otherNames=payload["otherNames"]
            surName=payload["surName"]
            bankType=payload["bankType"]
            iBan=payload["iBan"]
            friendlyName=payload["friendlyName"]
            bic=payload["bic"]
            beneficiary=payload["beneficiary"]
            beneficiaryAddress=payload["beneficiaryAddress"]

            account = db.query(Account).filter(Account.accountNumber == accountNo).first()

            if account is None:
                return {"status_code":401,"message":"account number doesn't exist"}
            elif not account.currency == currency:
                return {"status_code":401,"message":"currency doesn't match account currency"}
                
                
            

            bank = addBank(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan,bic,beneficiary,beneficiaryAddress)
            if not bank["status_code"] == 201:
                return bank
            db.commit()
            
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201, "token":token,"message":"linked bank account created successfully"}

@router.post("/getBanks")
async def createBank(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
                
            
            accountNo=payload["accountNo"]

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            bank = db.query(Bank).filter(Bank.accountNumber == accountNo).all()

            if len(bank) == 0:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201, "token":token,"message":bank}

@router.post("/getBanksIban")
async def createBank(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            
            
            iBan=payload["iBan"]
            bank = db.query(Bank).filter(Bank.iBan == iBan).first()
            accountNo=bank.accountNumber
            

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            

            if bank is None:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201, "token":token,"message":bank}

@router.post("/bankB")
async def createBank(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            
            accountNo=payload["accountNo"]
            bankName=payload["bankName"]
            country=payload["country"]
            currency=payload["currency"]
            otherNames=payload["otherNames"]
            surName=payload["surName"]
            bankType=payload["bankType"]
            iBan=payload["iBan"]
            friendlyName=payload["friendlyName"]
            bic=payload["bic"]
            beneficiary=payload["beneficiary"]
            beneficiaryAddress=payload["beneficiaryAddress"]

            account = db.query(Account).filter(Account.accountNumber == accountNo).first()

            if account is None:
                return {"status_code":401,"message":"account number doesn't exist"}
            elif not account.currency == currency:
                return {"status_code":401,"message":"currency doesn't match account currency"}
                
                
            

            bank = addBankB(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan)
            if not bank["status_code"] == 201:
                return bank
            db.commit()
            
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201, "token":token,"message":"linked bank account created successfully"}        

@router.post("/getBanksB")
async def createBank(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            
            
            accountNo=payload["accountNo"]
            friendlyName=payload["friendlyName"]

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            bank = db.query(BankBusiness).filter(BankBusiness.accountNumber == accountNo).all()

            if len(bank) == 0:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201, "token":token,"message":bank}        

@router.post("/getBanksBIban")
async def createBank(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
        try:
            payload = await request.body()
            # payload = json.loads(payload)
            # payload = payload['message']
            payload = json.loads(payload)
            token = payload['token']

        
            print('payload:',payload)
            
            
            bank = db.query(BankBusiness).filter(BankBusiness.iBan == payload["iBan"]).first()
            accountNo=bank.accountNumber
            

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            

            if len(bank) == 0:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201, "token":token,"message":bank,"account":account}        

@router.post("/inTransaction")
async def testT(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)


        print('payload:',payload)
        t = TransactionRequestIncoming(dateTime = datetime.now(),inIBan=payload["inIBan"],accountNo=payload["accountNo"],currency=payload["currency"],country=payload["country"],sendingCurrency=payload["sendingCurrency"],sendingCountry=payload["sendingCountry"],direction="in",transactionStatus="pending",amount=payload["amount"],feesCode=payload["feesCode"])
        db.add(t)
        db.commit()
        return {"status_code": 201,"message":"transaction request sent"}
    except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
@router.post("/balanceBank")
async def testT(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

            
        print('payload:',payload)
        t1 = db.query(Transaction).filter(Transaction.id%2 == 1).all()
        t2 = db.query(Transaction).filter(Transaction.id%2 == 0).all()

        transactions_data_1 = []
        for transaction in t1:
            transactions_data_1.append({
            'id': transaction.id,
            'dateTime': transaction.dateTime,
            'accountNo': transaction.fromAccountNo,
            'toAccountNo': transaction.toAccountNo,
            'transactionStatus': transaction.transactionStatus,
            'description': transaction.description,
            'amount': transaction.amount,
            'sendID': transaction.sendID,
            'recID': transaction.recID
        })
            
        transactions_data_2 = []
        for transaction in t2:
            transactions_data_2.append({
            'id': transaction.id,
            'dateTime': transaction.dateTime,
            'accountNo': transaction.fromAccountNo,
            'toAccountNo': transaction.toAccountNo,
            'transactionStatus': transaction.transactionStatus,
            'description': transaction.description,
            'amount': transaction.amount,
            'sendID': transaction.sendID,
            'recID': transaction.recID
        })
        
        
        df1 = pd.DataFrame(transactions_data_1)
        df2 = pd.DataFrame(transactions_data_2)

        df1['toAccountNo'] = df2['toAccountNo']
        df1['recID'] = df2['sendID']
        df1['description']=df2['description']
        df1.rename(columns={'accountNo': 'account paying','toAccountNo':'account receiving'}, inplace=True)
        df1["account receiving"][df1["account receiving"]=="10-00000005-001-00"]="Fees"
        df1["account receiving"][df1["account receiving"]=="10-00000003-001-00"]="OLW Bank"
        
        
        # df1['id'] = df1['id']/2+1
        print(df1)

        csv_file = 'transactions.csv'
        
        df1.to_csv(csv_file, index=False)
        
        

        return {"status_code": 201,"message":f"Data has been written to {csv_file}"}
    except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
def transactionOperation(identifier,sender,receiver,sendAmount,sendCurr,recCurr,db,displayName="None",merchantAccount = None):
    try:
        OLWAudit = db.query(Account).filter(Account.accountNumber == "10-00000001-001-00").first()
        
        now = datetime.now()
        recAmount = sendAmount * 1

        if OLWAudit is None:
            return {"status_code":401,"message":"Audit account not intialized"}
        
        accountSending = db.query(Account).filter(Account.accountNumber == sender).first()
        accountRec = db.query(Account).filter(Account.accountNumber == receiver).first()
        if accountSending is None and accountRec is None:
            return {"status_code":401,"message":"neither accounts is on OLW"}
        if accountSending is None:
            # if not checkExAccount(sender):
            #     return {"status_code":401,"message":"iBan does not exist"} 
            #

            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
            accountSending=OLWBank
            currency= db.query(Currency).filter(Currency.currencyName==recCurr).first()
            
            t1 = Transaction(dateTime=now,fromccountNo=OLWBank.accountNumber,toAccountNo=OLWAudit.accountNumber,sendID=OLWBank.customerID,recID=OLWAudit.customerID,transactionStatus="pending",amount=recAmount,description=sender,transactionIdentifier=identifier)
        else:
            t1 = Transaction(dateTime=now,fromAccountNo=accountSending.accountNumber,toAccountNo=OLWAudit.accountNumber,sendID=accountSending.customerID,recID=OLWAudit.customerID,transactionStatus="pending",amount=sendAmount,transactionIdentifier=identifier)   
        if sendAmount < 0:
            return {"status_code":401,"message":"sending amount can't be less than 0"}
        if sendAmount > accountSending.balance:
            return {"status_code":401,"message":"balance can't cover this transaction"}

        
        
        if accountRec is None:
            
            res  = checkExAccount(receiver)
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
            accountRec=OLWBank
            if not res["status_code"]==200:
                
                
                currency= db.query(Currency).filter(Currency.currencyName==recCurr).first()
                
                tr = TransactionRequest(dateTime=datetime.now(),accountNo=accountSending.accountNumber,outIBan=receiver,transactionStatus="pending",amount=sendAmount,currency=recCurr,country=currency.country,direction="out")
                db.add(tr)
                

            
            
            desc=receiver
            if not displayName == "None":
                desc = displayName
            if not merchantAccount == None:
                t2 = Transaction(dateTime=now,fromAccountNo=OLWAudit.accountNumber,toAccountNo=merchantAccount,sendID=OLWAudit.customerID,recID=OLWBank.customerID,transactionStatus="pending",amount=recAmount,description=desc,transactionIdentifier=identifier)
            else:
                t2 = Transaction(dateTime=now,fromAccountNo=OLWAudit.accountNumber,toAccountNo=OLWBank.accountNumber,sendID=OLWAudit.customerID,recID=OLWBank.customerID,transactionStatus="pending",amount=recAmount,description=desc,transactionIdentifier=identifier)
        else:
            t2 = Transaction(dateTime=now,fromAccountNo=OLWAudit.accountNumber,toAccountNo=accountRec.accountNumber,sendID=OLWAudit.customerID,recID=accountRec.customerID,transactionStatus="pending",amount=recAmount,transactionIdentifier=identifier)

            
        db.add(t1)
        db.add(t2)
        db.commit()

        
        db.refresh(t1)
        db.refresh(t2)
        
        db.query(Account).filter(Account.accountNumber == accountSending.accountNumber).update({"balance":accountSending.balance-sendAmount})
        db.query(Account).filter(Account.accountNumber == "2").update({"balance":OLWAudit.balance+sendAmount})

        db.query(Transaction).filter(Transaction.id == t1.id).update({"transactionStatus":"audit","counterPart":t2.id})
        db.query(Transaction).filter(Transaction.id == t2.id).update({"transactionStatus":"audit","counterPart":t1.id})

        db.query(Account).filter(Account.accountNumber == "2").update({"balance":OLWAudit.balance-recAmount})
        db.query(Account).filter(Account.accountNumber == accountRec.accountNumber).update({"balance":accountRec.balance+recAmount})

        db.query(Transaction).filter(Transaction.id == t1.id).update({"transactionStatus":"complete"})
        db.query(Transaction).filter(Transaction.id == t2.id).update({"transactionStatus":"complete"})
        db.commit()
        db.refresh(t1)
        db.refresh(t2)
    except:
        message = "exception occurred with creating transaction operation"
        log(0,message)
        return {"status_code":401,"message":message}
            
    return {"status_code":201,"message":"transaction operation complete","t1":t1.id,"t2":t2.id}

def checkExAccount(terminalNumber):
    r =requests.get("http://192.223.11.185:8080/terminal", json={'id': terminalNumber})
    return json.loads(r.content)

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
def addTranType(db,tCode,tName,desc = "None"):
    try:
        tO = db.query(TransactionType).filter(TransactionType.code == tCode,TransactionType.status == "active").first()
        if not tO is None:
            return {"status_code":401,"message":"code already exists"}
        tday = datetime.today()
        t= TransactionType(code = tCode,name = tName,status = "active",description = desc,number= 0,dd = tday.day,mm = tday.month,yy=tday.year%100)
        db.add(t)
        db.commit()
        return {"status_code":201,"message":"transaction type added successfully"}
    except:
        message = "exception occurred with creating transaction type"
        log(0,message)
        return {"status_code":401,"message":message}
    
def generateTranIdentifier(db,tcode):
    t = db.query(TransactionType).filter(TransactionType.code == tcode,TransactionType.status == "active").first()
    
    if t is None:
        return {"status_code":401,"message":"code does not exist"}
    today = datetime.today()
    if not(t.dd == today.day and t.mm == today.month and t.yy == today.year%100):
        db.query(TransactionType).filter(TransactionType.code == tcode,TransactionType.status == "active").update({"dd":today.day,"mm":today.month,"yy":today.year%100,"number":1})
        t.number=1
    else:
        db.query(TransactionType).filter(TransactionType.code == tcode,TransactionType.status == "active").update({"number":t.number+1})
    db.commit()
    returnString = tcode
    returnString += f"{int(today.day):02}"
    returnString += f"{int(today.month):02}"
    returnString += f"{int(today.year):02}"
    returnString += f"{int(t.number):08}"
    return {"status_code":201,"message":returnString}

def addFee(merchantID,categoryID,categoryName,categoryDescription,feeDescription,serviceCode,campaign,feeMax,feeMin,feeRate,feeFixed,db):
    try:
        mID = merchantID
        sCode = serviceCode
        fee = db.query(Fee).filter(Fee.merchantID == mID,Fee.serviceCode == sCode,Fee.status == "active").first()
        if not fee is None:
            return False
        f = Fee(merchantID=merchantID,categoryID=categoryID,categoryName=categoryName,categoryDescription=categoryDescription,feeDescription=feeDescription,serviceCode=serviceCode,campaign=campaign,status = "active",feeMax=feeMax,feeMin=feeMin,feeFixed=feeFixed,feeRate=feeRate)
    
        db.add(f)
        db.commit()
    except:
        message = "exception occurred with creating fees"
        log(0,message)
        return {"status_code":401,"message":message}
    return {"status_code":201,"message":"fee added successfully"}

def calcFee(db,amount,serviceCode,merchantID= "M001",campaignCode = "000"):
    try:
        sCode = serviceCode
        mID = merchantID
        cCode = campaignCode
        fee = db.query(Fee).filter(Fee.serviceCode==sCode,Fee.merchantID == str(mID),Fee.campaign == cCode,Fee.status == "active").first()
        if fee is None:
            fee = db.query(Fee).filter(Fee.serviceCode==sCode,Fee.merchantID == "M001",Fee.campaign == cCode,Fee.status == "active").first()
            if fee is None:
                return {"status_code":401,"message":"no fee exists with this code"}
        feeAmount = (fee.feeFixed+fee.feeRate/100*float(amount))
        if feeAmount>fee.feeMax and fee.feeMax>0:
            feeAmount = fee.feeMax
        if feeAmount<fee.feeMin:
            feeAmount = fee.feeMin
    except:
        message = "exception occurred with retrieving fee"
        log(0,message)
        return {"status_code":401,"message":message}
    
    return {"status_code":201,"fee":round(feeAmount,2)}

def addBank(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan,bic,ben,benAdd):
    try:
        bank = db.query(Bank).filter(Bank.iBan == iBan).first()
        if not bank is None:
            return {"status_code":401,"message":"bank already exists"}
        acc = db.query(Account).filter(Account.accountNumber == accountNo).first()
        if acc is None:
            return {"status_code":401,"message":"account doesn't exist"}
        bank = Bank(bankName=bankName,friendlyName=friendlyName,country=country,currency=currency,otherNames=otherNames,surName=surName,bankType=bankType,iBan=iBan,accountNumber=accountNo,bic=bic,beneficiary=ben,beneficiaryAddress=benAdd,shortDescription  ="Shor Description")
        db.add(bank)
    except:
        message = "exception occurred with retrieving banks"
        log(0,message)
        return {"status_code":401,"message":message}
    return {"status_code":201,"message":"bank added successfully"}

def addBankB(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan,bic,ben,benAdd):
    try:
        bank = db.query(BankBusiness).filter(BankBusiness.iBan == iBan).first()
        if not bank is None:
            return {"status_code":401,"message":"bank already exists"}
        acc = db.query(Account).filter(Account.accountNumber == accountNo).first()
        if acc is None:
            return {"status_code":401,"message":"account doesn't exist"}
        bank = BankBusiness(bankName=bankName,friendlyName=friendlyName,country=country,currency=currency,otherNames=otherNames,surName=surName,bankType=bankType,iBan=iBan,accountNo=accountNo,bic=bic,beneficiary=ben,beneficiaryAddress=benAdd)
        db.add(bank)
    except:
        message = "exception occurred with retrieving banks"
        log(0,message)
        return {"status_code":401,"message":message}
    return {"status_code":201,"message":"bank added successfully"}


def generateToken(id):
    time = datetime.now()+timedelta(minutes=15)
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    minute = time.minute
    zeroes = ["","","",""] #month,day,hour,minute
    if minute<10:
        zeroes[3]="0"
    if hour<10:
        zeroes[2]="0"
    if day<10:
        zeroes[1]="0"
    if month<10:
        zeroes[0]="0"
    intial = zeroes[3]+str(minute)+zeroes[0]+str(month)+zeroes[2]+str(hour)+str(year)+zeroes[1]+str(day)+str(id)
    final = ""
    for i in intial:
        final=final + str(9-int(i))
    return final

def checkToken(id,token):
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

def updateToken(id,db):
    try:
        token = db.query(Token).filter(Token.customerID ==id,Token.status=="active").first()
        if token==None:
            return False
        db.query(Token).filter(Token.customerID ==id,Token.status=="active").update({"token":generateToken(id),"expiration":datetime.now()+timedelta(minutes=tokenValidMins)})
        db.commit()
        token = db.query(Token).filter(Token.customerID ==id,Token.status=="active").first()
        
        return {"status_code":201,"message":token}
    except:
        message = "exception occurred with retrieving token"
        log(0,message)
        return {"status_code":401,"message":message}
    

    

@router.get("/currency")
async def testT(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        currencies = db.query(Currency).all()
        cur = []
        for i in currencies:
            cur.append(i.currency)
        return {"status_code":201,"currencies":cur}
    except:
        message = "exception occurred with retrieving currencies"
        log(0,message)
        return {"status_code":401,"message":message}
    
@router.get("/country")
async def testT(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        currencies = db.query(Currency).all()
        countries = []
        for i in currencies:
            countries.append(i.country)
        return {"status_code":201,"currencies":countries}
    except:
        message = "exception occurred with retrieving countries"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/getFees")
async def getFees(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

        if payload["feeCode"] == "00010003":
            payload["feeCode"] = "TF001"
            print("payload temp update") 
        print('payload:',payload)
        if not "merchantID" in payload:
            payload["merchantID"] = "M001"
        returning = calcFee(db,payload["amount"],payload["feeCode"],payload["merchantID"])
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        returning["level"] = cus.customerStatus
        if returning["level"]=="third level":
            returning["limit"]=lvl3Max
        elif returning["level"]=="second level":
            returning["limit"]=lvl2Max
        else:
            returning["limit"]=lvl1Max
        
        return returning 

            
    except:
        message = "exception occurred with retrieving fees"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/getEligibility")
async def getEle(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        

        returning = {}
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code":401,"message":"No customer exists with this ID"}
        
        returning["level"] = cus.customerStatus
        if returning["level"]=="third level":
            returning["limit"]=lvl3Max
        elif returning["level"]=="second level":
            returning["limit"]=lvl2Max
        elif returning["level"]=="first level":
            return {"status_code":401,"message":"User needs to finish KYC"}
        else:
            return {"status_code":401,"message":"User needs to confirm phone"}
        
        if payload["amount"]> returning["limit"]:
            return {"status_code":401,"message":"User level needs to increase to send this amount","level":returning["level"],"limit":returning["limit"]}

        return {"status_code":201,"message":"User eligibile to send this amount","level":returning["level"],"limit":returning["limit"],"token":token}

        
    except:
        message = "exception occurred with retrieving eligibility"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/charge")
async def charge(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)

        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code":401,"message":"No customer exists with this ID"}
        
        ch = addCharge(db,payload["id"],payload["currency"],payload["amount"],payload["feeService"],payload["feeCurrency"],payload["method"])
        if not ch["status_code"] == 201:
            return ch
        charge_instance = ch["message"]
        url = "http://192.223.11.185:9000/v1/card_process"
        # if charge.method == "crypto":
        #     url = "http://192.223.11.185:9000/v1/crypto_process"
        charge_dict = {
        'id': charge_instance.id,
        'dateTime': charge_instance.dateTime,
        'customerID': charge_instance.customerID,
        'accountNo': charge_instance.accountNo,
        'currency': charge_instance.currency,
        'amount': charge_instance.amount+charge_instance.feesService+charge_instance.feesCurrency,
        'feesService': charge_instance.feesService,
        'feesCurrency': charge_instance.feesCurrency,
        'email': charge_instance.email,
        'firstName': charge_instance.firstName,
        'lastName': charge_instance.lastName,
        'address': charge_instance.address,
        'zipcode': charge_instance.zipcode,
        'city': charge_instance.city,
        'country': charge_instance.country,
        'countryCode': charge_instance.countryCode,
        'mobilenumber': charge_instance.mobilenumber,
        'birthDate': charge_instance.birthDate,
        'chargeStatus': charge_instance.chargeStatus,
        'method': charge_instance.method,
        'transactionID': charge_instance.id,
        'webhookID': charge_instance.webhookID
        }
        if payload["method"]=="card":
            card = db.query(Card).filter(Card.token == payload["cardToken"]).first()
            if card is None:
                return {"status_code":401,"message":"no card with this token"}
            charge_dict["cardInfo"]={
                "cardNumber":card.cardNumber,
                "expMonth":card.expMonth,
                "expYear":card.expYear,
                "holderName":card.holderName,
                "secretNumber":card.secretNumber,
                "firstName":charge_instance.firstName,
                "lastName":charge_instance.lastName,
                "amount":charge_instance.amount
            }
            charge_dict["cardNumber"]=card.cardNumber
            charge_dict["expMonth"]=card.expMonth
            charge_dict["expYear"]=card.expYear
            charge_dict["holderName"]=card.holderName
            charge_dict["secretNumber"]=card.secretNumber
            

        req = requests.post(url, json=json.dumps(charge_dict)) 
            
        return {"status_code":201,"url":json.loads(req.content),"charge":charge_instance,"token":token}
        
    except:
        message = "exception occurred with charge process"
        log(0,message)
        return {"status_code":401,"message":message}

@router.get("/getCharge")
async def getCharge(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']


        print('payload:',payload)

        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code":401,"message":"No customer exists with this ID"}
        
        ch = db.query(Charge).filter(Charge.id == payload["chargeID"]).first()
        if ch is None:
            return {"status_code":401,"message":"No charge exists with this ID"}
        elif not int(ch.customerID) == cus.id:
            return {"status_code":401,"message":"this charge does not belong to this customer"}
        time  = datetime.strptime(ch.dateTime, '%Y-%m-%d %H:%M:%S.%f')+timedelta(minutes=20)
        if datetime.now() > time:
            db.query(Charge).filter(Charge.id == payload["chargeID"]).update({"chargeStatus":"Cancelled / Timed Out"})
            db.commit()
            db.refresh(ch)
                
            return {"status_code":401,"charge":ch,"token":token,"message":"timed out"}
        return {"status_code":201,"charge":ch,"token":token,"time":20}

        
    except:
        message = "exception occurred with retrieving eligibility"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/addCard")
async def addcard(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        # token = payload['token']


        print('payload:',payload)
        ac = addCard(db,payload["id"],payload["cardNumber"],payload["expiryMonth"],payload["expiryYear"],payload["fName"]+" "+payload["lName"],payload["secretNumber"])
        if not ac["status_code"] == 201:
            with open("formTemplates/failure.html", "r") as file:
                html_content = file.read()
                html_content = html_content.replace('%status_code', str(ac["status_code"]))
                html_content = html_content.replace('%errorMessage', str(ac["message"]))
                
                
            return Response(content=html_content, media_type="text/html")
            
        with open("formTemplates/success.html", "r") as file:
            html_content = file.read()
            html_content = html_content.replace('%status_code', "201")
        return Response(content=html_content, media_type="text/html")

        
    except:
        message = "exception occurred with adding card"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/removeCard")
async def addcard(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        card = db.query(Card).filter(Card.token == payload["cardToken"],Card.cardStatus == "active").first()
        if card is None:
            return {"status_code":401,"message":"this is not an active card"}
        
        card = db.query(Card).filter(Card.token == payload["cardToken"]).update({"cardStatus":"inactive"})
        db.commit()
         
        return {"status_code":201,"message":"card removed","token":token}
    except:
        message = "exception occurred with adding card"
        log(0,message)
        return {"status_code":401,"message":message}



@router.get("/cardForm/{cusID}")
async def addcard(cusID,request: Request,response: Response,db: Session = Depends(get_db)):
    with open("formTemplates/cardInfo.html", "r") as file:
        html_content = file.read()
        html_content = html_content.replace('%cusID', str(AlphanumericConverter.decode(str(cusID))))
    return Response(content=html_content, media_type="text/html")

@router.post("/encodeID")
async def addcard(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

        
        print('payload:',payload)

        re = AlphanumericConverter.encode(payload["id"])
        return {"status_code":200,"message":re}
    except:
        message = "exception occurred with encoding id"
        log(0,message)
        return {"status_code":401,"message":message}


@router.get("/getCards")
async def getcard(request: Request,response: Response,payload: dict = Body(...),db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        # payload = json.loads(payload)
        # payload = payload['message']
        payload = json.loads(payload)
        token = payload['token']

    
        print('payload:',payload)
        cards = db.query(Card).filter(Card.customerID == str(payload["id"]),Card.cardStatus == "active").all()
        extracted_details = []
        for card in cards:
            details = {
                'id': card.id,
                'dateTime': card.dateTime,
                'customerID': card.customerID,
                'token': card.token,
                'holderName': card.holderName,
                'last4digits': card.cardDescription  
            }
            extracted_details.append(details)

        return {"status_code":201,"message":extracted_details,"token":token}

            
    except:
        message = "exception occurred with getting card"
        log(0,message)
        return {"status_code":401,"message":message}


#x = await requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": sendCus.id,"accountNo":sendAcc.accountNumber,"message":"transaction registered","transactionStatus":tra.transactionStatus,"transactionID":tra.id,"terminal":payload["terminal"],"amount":payload["amount"],"currency":payload["toCurrency"]})

@router.post("/chargeTransaction")
async def testT(request: Request,response: Response,db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        payload = json.loads(payload)
        # payload = payload['message']
        # payload = json.loads(payload)
        # token = payload['token']

    
        print('payload:',payload)
        idn = generateTranIdentifier(db,"CHR")
        if not idn["status_code"]==201:
                return idn
        OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-00").first()
        OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-00").first()
        
        chID = payload["chargeID"]
        charge = db.query(Charge).filter(Charge.id==chID).first()
        if charge is None:
            return {"status_code": 401,"message":"no charge with this ID"}
        cus = db.query(Customer).filter(Customer.id==charge.customerID).first()
        if cus is None:
            return {"status_code": 401,"message":"no customer for this charge"}
        
        acc = db.query(Account).filter(Account.customerID ==cus.id, Account.primaryAccount).first()
        if acc is None:
            return {"status_code": 401,"message":"this customer has no primary account"}
        if payload["status"] == "Waiting for buyer funds...":
            return {"status_code": 201,"message":"awaiting change in status"}
        elif payload["status"] == "Cancelled / Timed Out":
            db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"Cancelled / Timed Out"})
            db.commit()
            return {"status_code": 201,"message":"transaction cancelled/timed out"}
        
        payload["status"] #complete,cancelled,rejected,waiting for buyer
        
        if OLWBank is None or OLWBank is None:
            return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
        trans = transactionOperation(idn["message"],f"charge {str(charge.id)}",acc.accountNumber,charge.amount+charge.feesCurrency+charge.feesService,charge.currency,charge.currency,db)
        print(trans)
        if not trans["status_code"]==201:
            db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"failed"})
            db.commit()
            return trans
                    
        if charge.feesCurrency>0:
            trans2 = transactionOperation(idn["message"],acc.accountNumber,"10-00000005-001-00",charge.feesCurrency,charge.currency,charge.currency,db)
            
            if not trans2["status_code"]==201:
                db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"failedF1"})
                db.commit()
                return trans2
        
        if charge.feesService>0:
            trans3 = transactionOperation(idn["message"],acc.accountNumber,"10-00000005-001-00",charge.feesService,charge.currency,charge.currency,db)
            
            if not trans3["status_code"]==201:
                db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"failedF2"})
                db.commit()
                return trans3
    except:
        message = "exception occurred with creating transaction"
        log(0,message)
        return {"status_code":401,"message":message}
    log(1,"from:OLW bank, to:{acc.accountNumber}, amount:{charge.amount},sending currency:{charge.currency}, receiving currency:{charge.currency}")
    db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"Completed","transactionID":trans["t1"],"webhookID":payload["webhookID"]})
    

    db.commit()
    db.refresh(charge)
    return {"status_code": 201,"message":"transaction completed","charge":charge}

def addCard(db,custID,cardNum,expM,expY,name,secretNum):
    try:
        cus = db.query(Customer).filter(Customer.id == custID).first()
        if cus is None:
            return {"status_code":401,"message":"customer with this ID does not exist"}
        if not len(cardNum) == 16:
            return {"status_code":401,"message":"card length needs to be 16 digits long"}
        elif int(expM)>13:
            return {"status_code":401,"message":"not valid expiry month"}
        elif int(expM)<1:
            return {"status_code":401,"message":"not valid expiry month"}
        elif int(expY)<1:
            return {"status_code":401,"message":"not valid expiry year"}
        elif not len(secretNum) == 3:
            return {"status_code":401,"message":"not valid cvv"}
        # c1 = db.query(Card).filter(Card.cardNumber == cardNum).first()
        # if c1 is None:
        #     return {"status_code":401,"message":"a card is already being used with this number"}

        ######### CAN WE ADD SAME CARD TO DIFFERENT USERS?

        alphanumeric_characters = string.ascii_letters + string.digits
        
        tok = ''.join(random.choice(alphanumeric_characters) for _ in range(tokenLen))
        c = db.query(Card).filter(Card.token == tok).first()
        while not c is None:
            tok = ''.join(random.choice(alphanumeric_characters) for _ in range(tokenLen))
            c = db.query(Card).filter(Card.token == tok).first()
        
        ca = Card(dateTime=datetime.now(),customerID=custID,token=tok,cardNumber=cardNum,expMonth=expM,expYear=expY,holderName=name,secretNumber=secretNum,cardStatus="active",cardDescription=cardNum[-4:])
        
        db.add(ca)
        db.commit()
        db.refresh(ca)
        

        return {"status_code":201,"message":ca}
    except Exception as e:
        message = "exception occurred with creating card"
        log(0,message)
        return {"status_code":401,"message":message}

def addCharge(db,custID,curr,am,feeS,feeC,meth):
    try:
        cus = db.query(Customer).filter(Customer.id == custID).first()
        if cus is None:
            return {"status_code":401,"message":"customer with this ID does not exist"}
        a = db.query(Account).filter(Account.customerID == cus.id,Account.primaryAccount).first()
        if a is None:
            return {"status_code":401,"message":"customer with this ID does not have primary account"}
        k = db.query(KYC).filter(KYC.customerID == cus.id).first()
        if k is None:
            return {"status_code":401,"message":"customer with this ID does not have KYC"}
        ad = db.query(Address).filter(Address.customerID == cus.id).first()
        if ad is None:
            return {"status_code":401,"message":"customer with this ID does not have address"}
        # m = db.query(Mobile).filter(Mobile.customerID == cus.id).first()
        # if m is None:
        #     return {"status_code":401,"message":"customer with this ID does not have mobile"}
        
        c = Charge(dateTime=datetime.now(),customerID=cus.id,accountNo=a.accountNumber,currency=curr,amount=am,feesService=feeS,feesCurrency=feeC,email=cus.email,firstName=cus.firstName,lastName=cus.lastName,address=ad.address1,zipcode=ad.zipCode,city=ad.city,country=ad.country,countryCode=cus.countryCode,mobilenumber=cus.phoneNumber,birthDate=k.birthDate,chargeStatus="pending",method=meth)
        db.add(c)
        db.commit()
        db.refresh(c)

        return {"status_code":201,"message":c}
    except:
        message = "exception occurred with creating charge"
        log(0,message)
        return {"status_code":401,"message":message}
    

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