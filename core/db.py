import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URL")  # Change this for production
DB_NAME = os.getenv("MONGO_DATABASE")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["Users"]
