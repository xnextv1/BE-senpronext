import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv

from models.users import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")  # Make sure this is set in your .env

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_jwt_token(user: User) -> str:
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "iat": datetime.datetime.utcnow(),
        "sub": str(user.user_id),  # make sure it's a string
        "user": {
            "email": user.email,
            "user_type": user.user_type,
            "username": user.username,
        }
    }
    return jwt.encode(payload, key=SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def decode_jwt_token(token: str) -> any:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return "Token is expired"
    except jwt.InvalidTokenError:
        return "Token is invalid"
    except Exception as e:
        return f"Error encountered: {str(e)}"
