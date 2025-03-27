from urllib import request

from pydantic import BaseModel
from routes.users import get_user_by_email, create_user
from core.security import verify_password, create_jwt_token, hash_password
from core.db import get_db
from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str


# Register a new user
@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db) ):
    existing_user = await get_user_by_email(request.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    await create_user(email=request.email, password=request.password, db=db)
    return {"message": "User registered successfully"}


# Login user and return JWT token
@router.post("/login")
async def login(request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):  # Add response parameter
    user = await get_user_by_email(request.email, db)

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(request.email)

    # Set cookie properly
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=3600
    )

    return {"access_token": token, "token_type": "bearer"}
