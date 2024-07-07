
from fastapi import FastAPI
from core.config import settings
from db.session import  engine,get_db
from db.base import Base
import asyncio
from apis.version3.processing import router as processing_router
from apis.version3.transactions import router as transaction_router
from apis.version3.autoOperations import router as background_router
from apis.version3.autoOperations import periodic_task


def create_tables():
    Base.metadata.create_all(bind=engine)

def startapplication():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION,docs_url=None, redoc_url=None)
    app.include_router(processing_router)
    app.include_router(transaction_router)
    app.include_router(background_router)
    
    db = next(get_db()) 

    create_tables()
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_task(db))
    return app


app = startapplication()





