from fastapi import APIRouter, Depends, HTTPException, Request
from app.account.services import create_user, authenticate_user, email_verification, verify_email_token
from app.account.models import UserCreate, UserOut
from app.db.config import SessionDep
from fastapi.security import OAuth2PasswordRequestForm
from app.account.auth import create_tokens, verify_refresh_token, revoke_refresh_token
from fastapi.responses import JSONResponse
from app.account.dependencies import get_current_user
import os

router = APIRouter(prefix="/account", tags=["Account"])

# Get secure flag from environment (True for production)
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"


@router.post("/register", response_model=UserOut)
async def user_register(session: SessionDep, user: UserCreate):
    return create_user(session, user)


@router.post("/login")
async def user_login(
    session: SessionDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    tokens = create_tokens(session, user)
    response = JSONResponse(content={
        "access_token": tokens["access_token"],
        "token_type": "bearer"
    })
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=SECURE_COOKIES,  # True in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )
    return response


@router.post("/refresh")
async def refresh_token(session: SessionDep, request: Request):
    old_token = request.cookies.get("refresh_token")
    if not old_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    user = verify_refresh_token(session, old_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # Revoke old refresh token (token rotation)
    revoke_refresh_token(session, old_token)
    
    # Create new tokens
    tokens = create_tokens(session, user)
    response = JSONResponse(content={
        "access_token": tokens["access_token"],
        "token_type": "bearer"
    })
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    return response


@router.get("/me", response_model=UserOut)
def me(user = Depends(get_current_user)):
    return user



@router.post("/logout")
async def logout(session: SessionDep, request: Request):
    token = request.cookies.get("refresh_token")
    if token:
        revoke_refresh_token(session, token)
    
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="refresh_token")
    return response

@router.post("/verify-request")
def send_verification_email(user = Depends(get_current_user)):
    return email_verification(user)

@router.get("/verify")
def verify_email(session: SessionDep, token: str):
    return verify_email_token(session, token)
    



# from fastapi import APIRouter, Depends, HTTPException, Request
# from app.account.services import create_user, authenticate_user
# from app.account.models import UserCreate, UserOut
# from app.db.config import SessionDep
# from fastapi.security import OAuth2PasswordRequestForm
# from app.account.auth import create_tokens, verify_refresh_token
# from fastapi.responses import JSONResponse


# router = APIRouter(prefix="/account", tags=["Account"])




# # Register User Route
# @router.post("/register", response_model=UserOut)
# async def user_register(session: SessionDep, user: UserCreate):
#   return create_user(session, user)


# # Login User Route
# @router.post("/login")    # response_model=UserOut filhal ka liye remove kiya ha
# async def user_login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends() ):
#   user = authenticate_user(session,form_data.username, form_data.password )
  
#   if not user:
#     raise HTTPException(status_code=400, detail="Invalid Credentials")
#   tokens = create_tokens(session, user )
#   response = JSONResponse(content={"access_token": tokens["access_token"]})
#   response.set_cookie(
#     "refresh_token", tokens["refresh_token"], 
#     httponly=True, 
#     secure=False, 
#     samesite="lax") # secure=False rakha ha abi
#   return response


# @router.post("/refresh")
# async def refresh_token(session: SessionDep, request: Request):
#   token = request.cookies.get("refresh_token")
#   if not token:
#     raise HTTPException(status_code=401, detail="Missing Refresh token")
#   user = verify_refresh_token(session, token)
#   if not user:
#     raise HTTPException(status_code=401, detail="Invalid or expired token")
#   return create_tokens(session, user)

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
  