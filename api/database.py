from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
from .config import settings

# Construct database URL
db_path = settings.database.path
if not os.path.isabs(db_path):
    # If relative, make it relative to project root or data dir
    # Assuming project root is where we run from
    db_path = os.path.abspath(db_path)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Check if we need to ensure directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool if ":memory:" in db_path else None
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models here so they are registered with Base
    # from . import models  # We will create models later
    Base.metadata.create_all(bind=engine)
