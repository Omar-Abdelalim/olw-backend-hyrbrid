from fastapi import APIRouter, Depends, Header, Request, Body, Response, status, HTTPException, FastAPI, Request
from sqlalchemy.orm import Session
from db.session import get_db
import base64
from starlette.middleware.base import BaseHTTPMiddleware
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import padding as pa
from db.globals.globals import tokens
import os
import json
from starlette.responses import JSONResponse
from datetime import datetime,timedelta
import random
import string
import logging

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session_expiry_time = 10

def encrypt(body, sessionID):
    t = tokens[sessionID]
    print(t)
    GLOBAL_KEY = base64.b64decode(t['key'])
    GLOBAL_IV = os.urandom(12)
    encrypter = Cipher(
        algorithms.AES(GLOBAL_KEY),
        modes.GCM(GLOBAL_IV),
        backend=default_backend()
    ).encryptor()

    message_bytes = body.encode()

    # Add padding to the message
    padder = pa.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message_bytes) + padder.finalize()

    encrypted = encrypter.update(padded_data) + encrypter.finalize()
    tag = encrypter.tag

    encrypted_message_base64 = base64.b64encode(encrypted).decode("utf-8")
    iv_base64 = base64.b64encode(GLOBAL_IV).decode("utf-8")
    tag_base64 = base64.b64encode(tag).decode("utf-8")

    return {
        'encrypted_message': encrypted_message_base64,
        'iv': iv_base64,
        'tag': tag_base64
    }
def load_private_key():
    with open("keys/private_key.pem", "rb") as private_key_file:
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password=None
        )
    return private_key


def load_public_key():
    with open("keys/public_key.pem", "rb") as public_key_file:
        public_key = serialization.load_pem_public_key(
            public_key_file.read()
        )
    return public_key

def decrypt_data(encrypted_data: str) -> bytes:
    private_key = load_private_key()
    encrypted_data_bytes = base64.b64decode(encrypted_data.encode())
    decrypted_data = private_key.decrypt(
        encrypted_data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

class DecryptRequest(BaseModel):
    message: str


class decryptMiddleware(BaseHTTPMiddleware):
    def decrypt_message_again(self, data: DecryptRequest):
        from fastapi.responses import JSONResponse
        # try:
        if not data.message:
            raise HTTPException(status_code=400, detail="encrypted_data field is required")
        decrypted_message = decrypt_data(data.message).decode()
        # except HTTPException as e:
        #     return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        # except Exception as e:
        #     return JSONResponse(status_code=500, content={"detail": f"Unexpected error: {str(e)}"})
        plaintext2_str = decrypted_message

        return {"message": plaintext2_str}

    async def dispatch(self, request: Request, call_next):
        requested_url = request.url.path
        if requested_url == "/initAccts" or requested_url == "/initOpts" or requested_url == "/confirmEmail" or requested_url == "/confirmMobile" or requested_url ==  "/resendVer" or requested_url == "/addCard" or requested_url == "/chargeTransaction":
            response = await call_next(request)
            return response
        if  ('/updateEmail/'in requested_url) or ('/email/' in requested_url) or ('/cardForm/'in requested_url):
            response = await call_next(request)
            return response
        
        
        
        body = await request.body()
        json_body = json.loads(body)
        print("body from request",json_body)
        substrings = json_body['message'].split(":::")
        alldicts = []
        for i in substrings:
            json_body = {'message':i}
            decrypt_request = DecryptRequest(**json_body)
            decrypted_message = self.decrypt_message_again(decrypt_request)
            modified_body =  json.dumps(decrypted_message).encode('utf-8') # Modify if necessary
            alldicts.append(modified_body)
        
        modified_body = ""
        print('alldicts:',alldicts)
        for j in alldicts:
            on = j
            on = on.decode('utf-8')
            
            if not requested_url == "/handshake":
                on = json.loads(on)
                on = on['message']
                print('on inside:',on)
                if 'token' in on:
                    if not on['token'] in tokens:
                        return {"status_code": 401, "message": "do handshake, token not stored"}
                else:
                    return {"status_code": 401, "message": "do handshake, token not stored"}
                # on = json.loads(on)
            print("ON:",on)
            modified_body=modified_body+on
        print('modefied',modified_body)
        
        # modified_body=json.dumps(modified_body).encode('utf-8')
        modified_body=modified_body.encode('utf-8')
        # Define a new receive function that returns the modified body
        async def receive() -> dict:
            return {"type": "http.request", "body": modified_body}

        request = Request(scope=request.scope, receive=receive)
        
        
        b=await request.body()
        print("body sent:",type(b),b)
        if not requested_url == '/handshake':    
            on = json.loads(b)    
            print('not handshake, body now: ',on)
            if not on['token'] in tokens:
                return {"status_code": 401, "message": "do handshake again"}


            if datetime.now() > tokens[on['token']]['exp']:
                del tokens[on['token']]
                return {"status_code": 401, "message": "do handshake again"}
            
            if not tokens[on['token']]['ip'] == request.client.host:
                del tokens[on['token']]
                return {"status_code": 401, "message": "do handshake again"}

        
        response = await call_next(request)
        if requested_url == "/test":
            return response
        # out_resp = encrypt(response,request.client.host)
        response_body = [section async for section in response.__dict__['body_iterator']]
        response_body_str = b"".join(response_body).decode('utf-8')
        print("reponse body: ",json.loads(response_body_str))
        respBody = json.loads(response_body_str)
        

        # out_resp = response_body_str#encrypt(response_body_str,request.client.host)
        curr_code = on
        if not requested_url == '/handshake':
            tokens[on['token']]['exp'] = datetime.now() + timedelta(minutes=session_expiry_time)
            curr_code = on['token']
            out_resp = encrypt(response_body_str,curr_code)
        else:
            out_resp = encrypt(response_body_str,respBody['session key'])
        return JSONResponse(content=out_resp)