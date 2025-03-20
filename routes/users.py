from core.db import users_collection
from core.security import hash_password

# Find user by username
async def get_user(username: str):
    return await users_collection.find_one({"username": username})

# Create a new user
async def create_user(username: str, password: str):
    hashed_password = hash_password(password)
    user_data = {"username": username, "hashed_password": hashed_password}
    await users_collection.insert_one(user_data)
