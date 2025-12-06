from app.account.models import User, RefreshToken, UserCreate, UserOut
from sqlmodel import Session, select
from fastapi import HTTPException
from app.account.auth import hash_password, verified_password, create_email_verification_token, verify_token_and_get_user_id


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


def email_verification(user: User):
  token = create_email_verification_token(user.id)
  link = f"http://localhost:8000/account/verify?token={token}"
  print(f"Verify your email:{link} ")
  return { "msg" : "Verification email sent"}

def verify_email_token(session: Session, token : str):
  user_id = verify_token_and_get_user_id(token, "verify")
  if not user_id:
    raise HTTPException(status_code=400, detail="Invalid or expired token ")
  stmt = select(User).where(User.id == user_id)
  user = session.exec(stmt).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  user.is_verified = True
  session.add(user)
  session.commit()
  return { "msg" : "Email Verified Successfully"}
  

  
  