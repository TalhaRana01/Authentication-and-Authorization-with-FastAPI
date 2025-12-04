from fastapi import APIRouter
from app.account.services import create_user
from app.account.models import UserCreate, UserOut
from app.db.config import SessionDep



router = APIRouter(prefix="/account", tags=["Account"])


# @router.get("/")
# async def root():
#   return {"message": " Account "}


@router.post("/regiser", response_model=UserOut)
async def user_register(session: SessionDep, user: UserCreate):
  return create_user(session, user)
