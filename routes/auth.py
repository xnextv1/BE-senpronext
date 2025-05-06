from urllib import request

from pydantic import BaseModel
from routes.users import get_user_by_email, create_user
from core.security import verify_password, create_jwt_token, hash_password, decode_jwt_token
from core.db import get_db
from fastapi import APIRouter, HTTPException, Response, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    userType: str


# Register a new user
@router.post("/register")
async def register(request: RegisterRequest, response :  Response,db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(request.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    await create_user(email=request.email, password=request.password, usertype = request.userType, db=db, db=db)
    user = await get_user_by_email(request.email, db)


    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_jwt_token(user)

    response.set_cookie(
        key="token",
        value=token,
        httponly=False,
        max_age=3600,  # 1 hour
        path="/",
        samesite="lax",
        secure=False
    )

    return {"message": "User registered successfully", "token": token}


# Login user and return JWT token
@router.post("/login")
async def login(request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(request.email, db)

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(user)
    refresh_token = create_jwt_token(user)

    # Set cookie for local development (adjust for production)
    response.set_cookie(
        key="token",
        value=token,
        httponly=False,
        max_age=3600,         # 1 hour
        path="/",
        samesite="lax",       # allow cookie on top-level navigation and fetch
        secure=False          # MUST be False if not using HTTPS
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=3600,
        path="/",
        samesite="lax",
        secure=False

    )
    return {"message": "Login successful"}



@router.get("/me")
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    decoded_token = decode_jwt_token(token)
    user = await get_user_by_email(decoded_token["user"]["email"], db)
    return {
        "username": user.username,
        "user_type": user.user_type,
        "email": user.email,
        "user_id": user.user_id,
        }