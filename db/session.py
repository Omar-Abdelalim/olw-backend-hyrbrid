from sqlalchemy import create_engine
from sqlalchemy.orm import session, sessionmaker
from core.config import settings
from typing import Generator

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

POOL_SIZE    = 10      # Number of connections to keep in the pool
MAX_OVERFLOW = 20      # Max number of connections to allow beyond POOL_SIZE
POOL_TIMEOUT = 30      # Timeout in seconds to get a connection from the pool
POOL_RECYCLE = 3600    # Recycle connections after this many seconds (to avoid issues with long-lived connections)

# Create the engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    echo=True,  # Optional: prints SQL queries (useful for debugging)
)

SessionLocal = sessionmaker(autocommit = False,autoflush=False,bind=engine)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
