
from fastapi import FastAPI
from core.config import settings
from db.session import  engine,get_db
from db.base import Base
import asyncio
from apis.version2.processing import router as processing_router
from apis.version2.transactions import router as transaction_router
from apis.version2.vcard import router as vcard_router
from autoOperations import periodic_task

from apis.version2.middleware import decryptMiddleware

active_session = {}

def create_tables():
    Base.metadata.create_all(bind=engine)

def startapplication():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION,docs_url=None, redoc_url=None)
    app.add_middleware(decryptMiddleware)
    app.include_router(processing_router)
    app.include_router(vcard_router)
    app.include_router(transaction_router)
    
    db = next(get_db()) 

    create_tables()
    # loop = asyncio.get_event_loop()
    # loop.create_task(periodic_task(db))
    return app


app = startapplication()





