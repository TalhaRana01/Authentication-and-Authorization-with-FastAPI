from app.account.models import User, RefreshToken, UserCreate, UserOut
from sqlmodel import Session, select
from fastapi import HTTPException
from app.account.auth import hash_password, verified_password


# User Register Logic
def create_user(session: Session, user: UserCreate):
  
  isEmailExist = select(User).where(User.email == user.email) 
  
  if session.exec(isEmailExist).first():
      raise HTTPException(status_code=400, detail="Email Already Exist")
  
    # function parameters
  new_user = User(
      name=user.name,
      email=user.email,
      hashed_password=hash_password(user.password),
      is_verified=False
      
      
    )
    # SQLMODEL Function
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  return new_user


# User Authentication 
def authenticate_user(session: Session, email : str, password : str):
  userEmail = select(User).where(User.email == email)
  user = session.exec(userEmail).first()
  if not user or not verified_password(password, user.hashed_password):
    return None
  return user
  
  