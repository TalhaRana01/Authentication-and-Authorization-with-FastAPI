from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from sqlmodel import Session
from app.account.models import RefreshToken, User
import uuid


SECRET_KEY = "secret1122"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Hash User Password
def hash_password(password:str):
  return pwd_context.hash(password)


# Verify User Password
def verified_password(plain_password, hash_password):
  return pwd_context.verify(plain_password, hash_password)



def create_access_token(data: dict, expires_delta: timedelta = None):
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM )
  

def create_tokens(session:Session, user: User):
  access_token = create_access_token(data={"sub" : str(user.id)})
  refresh_token_str = str(uuid.uuid4())
  expires_at = datetime.now(timezone.utc) + timedelta(days=7)
  refresh_token = RefreshToken(
    user_id = user.id,
    token = refresh_token_str,
    expires_at= expires_at
  )
  
  session.add(refresh_token)
  session.commit()
  return {
    "access_token" : access_token,
    "refresh_token" : refresh_token,
    "token_type" : "bearer"
  }
  
  