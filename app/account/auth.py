from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from sqlmodel import Session, select
from app.account.models import RefreshToken, User
import uuid
import os

# Load from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password"""
    return pwd_context.hash(password)


def verified_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_tokens(session: Session, user: User) -> dict:
    """Create both access and refresh tokens for a user"""
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Create refresh token
    refresh_token_str = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=expires_at,
        revoked=False
    )
    
    session.add(refresh_token)
    session.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    }


def verify_refresh_token(session: Session, token: str):
    """Verify a refresh token and return the associated user"""
    statement = select(RefreshToken).where(RefreshToken.token == token)
    db_token = session.exec(statement).first()
    
    if not db_token or db_token.revoked:
        return None
    
    # Ensure timezone awareness
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    # Check if token is expired
    if expires_at <= datetime.now(timezone.utc):
        return None
    
    # Get user
    stmt = select(User).where(User.id == db_token.user_id)
    return session.exec(stmt).first()


def revoke_refresh_token(session: Session, token: str) -> bool:
    """Revoke a refresh token (for logout or token rotation)"""
    statement = select(RefreshToken).where(RefreshToken.token == token)
    db_token = session.exec(statement).first()
    
    if db_token:
        db_token.revoked = True
        session.add(db_token)
        session.commit()
        return True
    return False


def cleanup_expired_tokens(session: Session) -> int:
    """Delete expired refresh tokens from database"""
    statement = select(RefreshToken).where(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    )
    expired_tokens = session.exec(statement).all()
    
    for token in expired_tokens:
        session.delete(token)
    
    session.commit()
    return len(expired_tokens)


def decode_token(token: str):
    
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM )
    except JWTError:
        return None 


# from app.account.models import User, UserCreate
# from sqlmodel import Session, select
# from fastapi import HTTPException
# from app.account.auth import hash_password, verified_password


# def create_user(session: Session, user: UserCreate) -> User:
#     # Check if email exists
#     statement = select(User).where(User.email == user.email)
#     existing_user = session.exec(statement).first()
    
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create new user
#     new_user = User(
#         name=user.name,
#         email=user.email,
#         hashed_password=hash_password(user.password),
#         is_verified=False
#     )
    
#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)
#     return new_user


# def authenticate_user(session: Session, email: str, password: str) -> User | None:
#     statement = select(User).where(User.email == email)
#     user = session.exec(statement).first()
    
#     if not user or not verified_password(password, user.hashed_password):
#         return None
    
#     return user










# from passlib.context import CryptContext
# from datetime import timedelta, datetime, timezone
# from jose import jwt, JWTError
# from sqlmodel import Session, select
# from app.account.models import RefreshToken, User
# import uuid
# import os

# # Load from environment variables
# SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
# REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)


# def verified_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


# def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (
#         expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     )
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def create_tokens(session: Session, user: User) -> dict:
#     # Create access token
#     access_token = create_access_token(data={"sub": str(user.id)})
    
#     # Create refresh token
#     refresh_token_str = str(uuid.uuid4())
#     expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
#     refresh_token = RefreshToken(
#         user_id=user.id,
#         token=refresh_token_str,
#         expires_at=expires_at,
#         revoked=False
#     )
    
#     session.add(refresh_token)
#     session.commit()
    
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token_str,
#         "token_type": "bearer"
#     }


# def verify_refresh_token(session: Session, token: str) -> User | None:
#     statement = select(RefreshToken).where(RefreshToken.token == token)
#     db_token = session.exec(statement).first()
    
#     if not db_token or db_token.revoked:
#         return None
    
#     # Ensure timezone awareness
#     expires_at = db_token.expires_at
#     if expires_at.tzinfo is None:
#         expires_at = expires_at.replace(tzinfo=timezone.utc)
    
#     # Check if token is expired
#     if expires_at <= datetime.now(timezone.utc):
#         return None
    
#     # Get user
#     stmt = select(User).where(User.id == db_token.user_id)
#     return session.exec(stmt).first()


# def revoke_refresh_token(session: Session, token: str) -> bool:
#     """Revoke a refresh token (for logout or token rotation)"""
#     statement = select(RefreshToken).where(RefreshToken.token == token)
#     db_token = session.exec(statement).first()
    
#     if db_token:
#         db_token.revoked = True
#         session.add(db_token)
#         session.commit()
#         return True
#     return False


# def cleanup_expired_tokens(session: Session) -> int:
#     """Delete expired refresh tokens from database"""
#     statement = select(RefreshToken).where(
#         RefreshToken.expires_at < datetime.now(timezone.utc)
#     )
#     expired_tokens = session.exec(statement).all()
    
#     for token in expired_tokens:
#         session.delete(token)
    
#     session.commit()
#     return len(expired_tokens)






# # from passlib.context import CryptContext
# # from datetime import timedelta, datetime, timezone
# # from jose import jwt, JWTError
# # from sqlmodel import Session, select
# # from app.account.models import RefreshToken, User
# # import uuid


# # SECRET_KEY = "secret1122"
# # ALGORITHM = "HS256"
# # pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# # # Hash User Password
# # def hash_password(password:str):
# #   return pwd_context.hash(password)


# # # Verify User Password
# # def verified_password(plain_password, hash_password):
# #   return pwd_context.verify(plain_password, hash_password)



# # def create_access_token(data: dict, expires_delta: timedelta = None):
# #   to_encode = data.copy()
# #   expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
# #   to_encode.update({"exp": expire})
# #   return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM )
  

# # def create_tokens(session:Session, user: User):
# #   access_token = create_access_token(data={"sub" : str(user.id)})
# #   refresh_token_str = str(uuid.uuid4())
# #   expires_at = datetime.now(timezone.utc) + timedelta(days=7)
# #   refresh_token = RefreshToken(
# #     user_id = user.id,
# #     token = refresh_token_str,
# #     expires_at= expires_at
# #   )
  
# #   session.add(refresh_token)
# #   session.commit()
# #   return {
# #     "access_token" : access_token,
# #     "refresh_token" : refresh_token_str,  # change refresh_token to refresh_token
# #     "token_type" : "bearer"
# #   }

# # def verify_refresh_token(session: Session, token : str):
# #   statement = select(RefreshToken).where(RefreshToken.token == token)
# #   db_token = session.exec(statement).first()
  
# #   if db_token and not db_token.revoked:
# #     expires_at = db_token.expires_at
# #     if expires_at.tzinfo is None:
# #       expires_at = expires_at.replace(tzinfo=timezone.utc)
# #     if expires_at > datetime.now(timezone.utc):
      
# #       stmt = select(User).where(User.id == db_token.user_id)  # user_id change ki ha 
# #       return session.exec(stmt).first()
# #   return None
  