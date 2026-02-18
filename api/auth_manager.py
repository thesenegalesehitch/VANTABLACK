"""
VANTABLACK Authentication Manager - Security & Authorization
=========================================================

Comprehensive authentication and authorization system:
- JWT token management
- Role-based access control
- API key authentication
- Session management
- Security policies
"""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import hashlib
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session as DBSession

from .database import SessionLocal, init_db
from .models import User, Session, APIKey
from .types import UserRole, Permission

class AuthManager:
    """Authentication and authorization manager with DB persistence"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
        self.session_expiry = timedelta(days=7)
        
        # Initialize DB tables
        init_db()
        
        # Role permissions mapping
        self.role_permissions = {
            UserRole.ADMIN: [p.value for p in Permission],
            UserRole.RED_TEAM: [
                Permission.TEMPLATE_CREATE.value, Permission.TEMPLATE_READ.value, Permission.TEMPLATE_UPDATE.value,
                Permission.CAMPAIGN_CREATE.value, Permission.CAMPAIGN_READ.value, Permission.CAMPAIGN_UPDATE.value, Permission.CAMPAIGN_EXECUTE.value,
                Permission.ANALYSIS_RUN.value, Permission.ANALYSIS_READ.value,
                Permission.MARKETPLACE_READ.value, Permission.MARKETPLACE_SUBMIT.value
            ],
            UserRole.ANALYST: [
                Permission.TEMPLATE_READ.value, Permission.CAMPAIGN_READ.value,
                Permission.ANALYSIS_RUN.value, Permission.ANALYSIS_READ.value,
                Permission.MARKETPLACE_READ.value
            ],
            UserRole.VIEWER: [
                Permission.TEMPLATE_READ.value, Permission.CAMPAIGN_READ.value,
                Permission.ANALYSIS_READ.value, Permission.MARKETPLACE_READ.value
            ]
        }
        
        # Initialize default admin user
        self._initialize_default_admin()
    
    def get_db(self):
        return SessionLocal()
        
    def _initialize_default_admin(self):
        db = self.get_db()
        try:
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                admin_password = self._hash_password("admin123")
                admin_user = User(
                    user_id="admin_default",
                    username="admin",
                    email="admin@vantablack.local",
                    password_hash=admin_password,
                    role=UserRole.ADMIN.value,
                    permissions=self.role_permissions[UserRole.ADMIN],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    last_login=None
                )
                # Note: models.py has permissions as JSON column
                # We need to ensure we pass it correctly.
                # In User model: permissions = Column(JSON)
                # So passing list is fine.
                db.add(admin_user)
                db.commit()
                logging.info("Default admin user created")
        except Exception as e:
            logging.error(f"Failed to create default admin: {e}")
        finally:
            db.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _generate_jwt_token(self, user: User, expires_delta: timedelta = None) -> str:
        """Generate JWT token for user"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + self.token_expiry
        
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "permissions": user.permissions,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access_token"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        return f"vk_{secrets.token_urlsafe(32)}"
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_user(self, username: str, email: str, password: str, 
                         role: UserRole = UserRole.RED_TEAM) -> str:
        """Create new user"""
        def _create():
            db = self.get_db()
            try:
                if db.query(User).filter((User.username == username) | (User.email == email)).first():
                    raise ValueError("User with this username or email already exists")
                
                user_id = f"user_{secrets.token_urlsafe(16)}"
                password_hash = self._hash_password(password)
                
                user = User(
                    user_id=user_id,
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role=role.value,
                    permissions=self.role_permissions[role],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    last_login=None
                )
                
                db.add(user)
                db.commit()
                logging.info(f"User created: {username} ({user_id})")
                return user_id
            finally:
                db.close()
                
        return await run_in_threadpool(_create)
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = "127.0.0.1",
                              user_agent: str = "Unknown") -> Optional[Dict[str, Any]]:
        """Authenticate user with username/password"""
        def _auth():
            db = self.get_db()
            try:
                user = db.query(User).filter(User.username == username).first()
                
                if not user or not user.is_active:
                    return None
                
                if not self._verify_password(password, user.password_hash):
                    return None
                
                # Update last login
                user.last_login = datetime.utcnow()
                
                # Create session
                session_id = secrets.token_urlsafe(32)
                session = Session(
                    session_id=session_id,
                    user_id=user.user_id,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + self.session_expiry,
                    last_activity=datetime.utcnow(),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_active=True
                )
                
                db.add(session)
                db.commit()
                
                token = self._generate_jwt_token(user)
                
                logging.info(f"User authenticated: {username} ({user.user_id})")
                
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "expires_in": int(self.token_expiry.total_seconds()),
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role,
                    "permissions": user.permissions,
                    "session_id": session_id
                }
            finally:
                db.close()
                
        return await run_in_threadpool(_auth)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            def _check_user():
                db = self.get_db()
                try:
                    user = db.query(User).filter(User.user_id == user_id).first()
                    if not user or not user.is_active:
                        return None
                    
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "permissions": user.permissions,
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat() if user.last_login else None
                    }
                finally:
                    db.close()
            
            return await run_in_threadpool(_check_user)
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            logging.warning(f"Token verification failed: {e}")
            return None
    
    async def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return user info"""
        key_hash = self._hash_api_key(api_key)
        
        def _verify():
            db = self.get_db()
            try:
                api_key_obj = db.query(APIKey).filter(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True
                ).first()
                
                if not api_key_obj:
                    return None
                
                if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                    return None
                
                user = db.query(User).filter(User.user_id == api_key_obj.user_id).first()
                if not user or not user.is_active:
                    return None
                
                api_key_obj.last_used = datetime.utcnow()
                db.commit()
                
                return {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "permissions": api_key_obj.permissions,
                    "api_key_id": api_key_obj.key_id,
                    "api_key_name": api_key_obj.name
                }
            finally:
                db.close()
        
        return await run_in_threadpool(_verify)
    
    async def create_api_key(self, user_id: str, name: str, 
                           permissions: List[Permission] = None,
                           expires_in_days: int = None) -> str:
        """Create API key for user"""
        def _create():
            db = self.get_db()
            try:
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise ValueError("User not found")
                
                api_key = self._generate_api_key()
                key_hash = self._hash_api_key(api_key)
                key_id = f"key_{secrets.token_urlsafe(16)}"
                
                perms = permissions if permissions else user.permissions
                if isinstance(perms, list) and perms and isinstance(perms[0], Permission):
                     perms = [p.value for p in perms]
                
                expires_at = None
                if expires_in_days:
                    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
                
                api_key_obj = APIKey(
                    key_id=key_id,
                    user_id=user_id,
                    key_hash=key_hash,
                    name=name,
                    permissions=perms,
                    created_at=datetime.utcnow(),
                    expires_at=expires_at,
                    last_used=None,
                    is_active=True
                )
                
                db.add(api_key_obj)
                db.commit()
                logging.info(f"API key created: {name} for user {user_id}")
                return api_key
            finally:
                db.close()
        
        return await run_in_threadpool(_create)
    
    async def revoke_api_key(self, user_id: str, key_id: str) -> bool:
        """Revoke API key"""
        def _revoke():
            db = self.get_db()
            try:
                api_key_obj = db.query(APIKey).filter(
                    APIKey.key_id == key_id,
                    APIKey.user_id == user_id
                ).first()
                
                if not api_key_obj:
                    return False
                
                api_key_obj.is_active = False
                db.commit()
                logging.info(f"API key revoked: {key_id} for user {user_id}")
                return True
            finally:
                db.close()
        
        return await run_in_threadpool(_revoke)
    
    async def check_permission(self, user_info: Dict[str, Any], 
                            required_permission: Permission) -> bool:
        """Check if user has required permission"""
        user_permissions = user_info.get("permissions", [])
        return required_permission.value in user_permissions
    
    async def check_role(self, user_info: Dict[str, Any], required_role: UserRole) -> bool:
        """Check if user has required role or higher"""
        user_role = UserRole(user_info.get("role", "viewer"))
        
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.ANALYST: 1,
            UserRole.RED_TEAM: 2,
            UserRole.ADMIN: 3
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

    # Added methods for consistency with rest_api usage if any missing
    async def invalidate_session(self, session_id: str) -> bool:
         def _invalidate():
            db = self.get_db()
            try:
                session = db.query(Session).filter(Session.session_id == session_id).first()
                if not session:
                    return False
                session.is_active = False
                db.commit()
                return True
            finally:
                db.close()
         return await run_in_threadpool(_invalidate)

    async def get_system_stats(self) -> Dict[str, Any]:
         def _stats():
            db = self.get_db()
            try:
                total_users = db.query(User).count()
                active_users = db.query(User).filter(User.is_active == True).count()
                total_sessions = db.query(Session).count()
                active_sessions = db.query(Session).filter(Session.is_active == True).count()
                
                # Role distribution
                roles = db.query(User.role).all()
                role_dist = {}
                for r in roles:
                    role_dist[r[0]] = role_dist.get(r[0], 0) + 1
                    
                return {
                    "users": {"total": total_users, "active": active_users, "role_distribution": role_dist},
                    "sessions": {"total": total_sessions, "active": active_sessions}
                }
            finally:
                db.close()
         return await run_in_threadpool(_stats)
