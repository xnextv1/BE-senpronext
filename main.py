from fastapi import FastAPI
from routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allowed origins (change this to your frontend's port)
origins = [
    os.getenv("FRONTEND_URL"),  # React/Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific frontend ports
    allow_credentials=True,  # Allow cookies (important for JWT auth)
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allowed HTTP methods
    allow_headers=["Content-Type", "Authorization"],  # Allowed headers
)


app.include_router(auth_router, prefix="/auth")



@app.get("/")
def home():
    return {"message": "FastAPI + MongoDB Authentication"}
