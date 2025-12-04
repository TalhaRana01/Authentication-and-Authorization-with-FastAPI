from fastapi import APIRouter, Depends, HTTPException
from app.account.services import create_user, authenticate_user
from app.account.models import UserCreate, UserOut
from app.db.config import SessionDep
from fastapi.security import OAuth2PasswordRequestForm
from app.account.auth import create_tokens
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/account", tags=["Account"])




# Register User Route
@router.post("/regiser", response_model=UserOut)
async def user_register(session: SessionDep, user: UserCreate):
  return create_user(session, user)


# Login User Route
@router.post("/login", response_model=UserOut)
async def user_login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends() ):
  user = authenticate_user(session,form_data.username, form_data.password )
  
  if not user:
    raise HTTPException(status_code=400, detail="Invalid Credentials")
  tokens = create_tokens(session, user )
  response = JSONResponse(content={"access_token": tokens["access_token"]})
  response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True, secure=True, samesite="lax")
  return response


# {
#   "email": "talha@gmail.com",
#   "name": "talha rana",
#   "is_active": true,
#   "is_admin": false,
#   "password": "rana1122"
# }

# {
  # "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzY0ODc1NDYwfQ.r5oNDQrj7VQ-O6NWnoTbC3Hi62lN6ssZe2b3vHxCkVw"
# }
  