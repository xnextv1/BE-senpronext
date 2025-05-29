from typing import Optional
from urllib import request

from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import select, func

from core.ai import get_emotional_recap
from models.chat import ChatMessage
from models.users import User
from routes.users import get_user_by_email, create_user, update_user_description_and_image, update_user_description
from core.security import verify_password, create_jwt_token, hash_password, decode_jwt_token
from core.db import get_db
from fastapi import APIRouter, HTTPException, Response, Depends, Request, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary.uploader
import os

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    userType: str

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)


# Register a new user
@router.post("/register")
async def register(request: RegisterRequest, response :  Response,db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(request.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    await create_user(username=request.username,email=request.email, password=request.password, usertype = request.userType, db=db)
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
        samesite="none",
        secure=True
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
        "description": user.description,
        "image": user.image,
        }

@router.get("/me/dashboard")
async def get_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Login required")

    decoded_token = decode_jwt_token(token)
    user = await get_user_by_email(decoded_token["user"]["email"], db)

    stmt = (
        select(ChatMessage.emotion, func.count().label("count"))
        .where(ChatMessage.user_id == user.user_id)
        .group_by(ChatMessage.emotion)
    )

    result = await db.execute(stmt)
    emotion_counts = result.all()

    return {
        "emotion_counts": [
            {"emotion": emotion, "count": count}
            for emotion, count in emotion_counts
        ]
    }

@router.get("/me/recap")
async def get_recap(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Login required")

    decoded_token = decode_jwt_token(token)
    user = await get_user_by_email(decoded_token["user"]["email"], db)
    response = await get_emotional_recap(user_id=user.user_id, db=db)

    return {"recap": response}

@router.patch("/profile/update")
async def update_profile(
    description: str = Form(...),
    user_id: int = Form(...),
    img: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    print(f"img: {img}, type: {type(img)}")
    if img:
        try:
            upload_result = cloudinary.uploader.upload(img.file)
            print("Cloudinary result:", upload_result)
            image_url = upload_result.get("secure_url")
            await update_user_description_and_image(db=db, user_id=user_id, description=description,
                                                        image=image_url)
        except Exception as e:
            return {"error": "Image upload failed", "details": str(e)}

    else:
        await update_user_description(db=db, user_id=user_id, description=description)

    return {"message": "Profile updated successfully"}