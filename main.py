
from fastapi import FastAPI, Request, HTTPException
from core.config import settings
from db.session import  engine,get_db
from db.base import Base
from apis.version2.processing import router as processing_router
from apis.version2.transactions import router as transaction_router
from apis.version2.vcard import router as vcard_router
from apis.version2.merchant_traansactions import router as merchant_transaction_router

from fastapi.responses import JSONResponse

from apis.version2.middleware import decryptMiddleware

active_session = {}

def create_tables():
    Base.metadata.create_all(bind=engine)
# Custom 404 handler
async def custom_404_handler(request: Request, exc: HTTPException):
    
    return JSONResponse(
        status_code=403,  # Returning 403 Forbidden instead of 404 Not Found
        content={"message": "Access Denied"},
    )

def startapplication():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION,docs_url=None, redoc_url=None)
    app.add_middleware(decryptMiddleware)
    app.include_router(processing_router)
    app.include_router(vcard_router)
    app.include_router(transaction_router)
    app.include_router(merchant_transaction_router)
    
    app.add_exception_handler(404, custom_404_handler)

    db = next(get_db()) 

    create_tables()
    # loop = asyncio.get_event_loop()
    # loop.create_task(periodic_task(db))
    return app



app = startapplication()





