from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from routes.users import get_user, create_user
from core.security import verify_password, create_jwt_token

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


# Register a new user
@router.post("/register")
async def register(request: RegisterRequest):
    existing_user = await get_user(request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    await create_user(request.username, request.password)
    return {"message": "User registered successfully"}


# Login user and return JWT token
@router.post("/login")
async def login(request: LoginRequest, response: Response):  # Add response parameter
    user = await get_user(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(request.username)

    # Set cookie properly
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=3600
    )

    return {"access_token": token, "token_type": "bearer"}
