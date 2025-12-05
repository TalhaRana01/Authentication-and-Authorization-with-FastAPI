from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from sqlmodel import select
from app.db.config import SessionDep
from app.account.auth import decode_token
from app.account.models import User


oauth2_schema = OAuth2PasswordBearer(tokenUrl='account/login')


def get_current_user(session: SessionDep, token : str = Depends(oauth2_schema) ):
  payload = decode_token(token)
  if not payload:
    raise HTTPException(status_code=401, detail="Invalid credentials")
  stmt = select(User).where(User.id == int(payload.get("sub")))
  user = session.exec(stmt).first()
  
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user
    