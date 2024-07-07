from fastapi import APIRouter,Depends,Header,Request,Body,Response, status,BackgroundTasks
from sqlalchemy.orm import Session
from db.session import get_db
from typing import Annotated
import json
import bcrypt
import random
import asyncio
import sched
import time
import httpx
from random import randrange
from datetime import datetime,timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template


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
from db.models.charge import Charge

import apis.version3.transactions as transactions

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
tokenValidMins = 15
chargePendingTime = 20


origins = [

    "http://localhost",
    "http://localhost:8080",
]

async def periodic_task(db: Session):

    # pend = db.query(EmailCode).filter(EmailCode.result == "pending").all()
    # for i in pend:
    #     if datetime.now() > datetime.strptime(i.expiration, '%Y-%m-%d %H:%M:%S.%f'):
    #         db.query(EmailCode).filter(EmailCode.id == i.id).update({"result":"expired"})
    
    db.commit()
    while True:
        print("checking outgoing transactions")
        try:
            tran = db.query(TransactionRequest).filter(TransactionRequest.transactionStatus == "pending" and TransactionRequest.direction=="out").first()
            
            while not tran is None:
                #operation to request sending money to that iBan
                log(1,"OUT GOING TRANSACTION from:{}, to:{}, amount:{}, currency:{}".format(tran.accountNo,tran.outIBan,tran.amount,tran.currency)) 
                db.query(TransactionRequest).filter(TransactionRequest.id == tran.id).update({"transactionStatus":"processed"})
                db.commit()
                tran=db.query(TransactionRequest).filter(TransactionRequest.transactionStatus == "pending").first()
            tran = db.query(TransactionRequestIncoming).filter(TransactionRequestIncoming.transactionStatus == "pending" and TransactionRequestIncoming.direction == "in").first()
            while not tran is None:
                log(1,"INCOMING TRANSACTION from:{}, to:{}, amount:{}, currency:{}".format(tran.inIBan,tran.accountNo,tran.amount,tran.currency)) 
                t = await transactions.tansaction3(tran.id,db)
                tran = db.query(TransactionRequestIncoming).filter(TransactionRequestIncoming.transactionStatus == "pending" and TransactionRequestIncoming.direction == "in").first()
            charges = db.query(Charge).filter(Charge.chargeStatus == "pending").all()
            for charge in charges:
                time  = datetime.strptime(charge.dateTime, '%Y-%m-%d %H:%M:%S.%f') +timedelta(minutes=chargePendingTime)
                if datetime.now() > time:
                    #send an api to request cancel
                    db.query(Charge).filter(Charge.id == charge.id).update({"chargeStatus":"Cancelled / Timed Out"})
                    db.commit()

        except:
            message = "exception occurred with outgoing transactions"
            log(0,message)
        # Your indefinite task logic goes here
        #response = await client.post("http://127.0.0.1:8000/outRequests")
        await asyncio.sleep(300)


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
    if not int(id)+int(revId) == 9:
        return False
    values= ""
    for i in token:
        values = values+ str(9-int(i))
    expiration = datetime(year=int(values[6:10]),month=int(values[2:4]),day=int(values[10:12]),hour=int(values[4:6]),minute=int(values[0:2]))
    if datetime.now()>expiration:
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
    

