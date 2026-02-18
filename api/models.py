from sqlalchemy import Column, String, Boolean, DateTime, JSON
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) 
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)
    is_active = Column(Boolean, default=True)

class APIKey(Base):
    __tablename__ = "api_keys"

    key_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    key_hash = Column(String)
    name = Column(String)
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
