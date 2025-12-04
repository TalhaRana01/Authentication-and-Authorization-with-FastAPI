from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.config import creat_tables
from app.account.models import User, RefreshToken


@asynccontextmanager
async def lifespan(app: FastAPI):
  creat_tables()
  yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
  return {"message" : "Server is running"}