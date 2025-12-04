from fastapi import APIRouter



router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/")
async def root():
  return {"message": " Account "}