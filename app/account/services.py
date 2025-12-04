from app.account.models import User, RefreshToken, UserCreate, UserOut
from sqlmodel import Session, select
from fastapi import HTTPException



def create_user(session: Session, user: UserCreate):
  
  isEmailExist = select(User).where(User.email == user.email) 
  
  if session.exec(isEmailExist).first():
    raise HTTPException(status_code=400, detail="Email Already Exist")
  
    # function parameters
  new_user = User(
      name=user.name,
      email=user.email,
      hashed_password=user.password,
      is_verified=False
      
      
    )
    # SQLMODEL Function
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  return new_user
  