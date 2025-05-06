from fastapi import FastAPI, Request, Response

from routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routes.chat import router as chat_router
from routes.article import router as article_router

load_dotenv()

app = FastAPI()

# Allowed origins (change this to your frontend's port)
origins = [
    os.getenv("FRONTEND_URL"),  # React/Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow specific frontend ports
    allow_credentials=True,  # Allow cookies (important for JWT auth)
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allowed HTTP methods
    allow_headers=["Content-Type", "Authorization", ],  # Allowed headers
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url} {request.client.host}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(article_router, prefix="/api/v1", tags=["Article"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

