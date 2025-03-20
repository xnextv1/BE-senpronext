from fastapi import FastAPI, HTTPException, Depends
import jwt
import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

app = FastAPI()

# Secret key for encoding and decoding JWT
SECRET_KEY = "4qQqEaKn6kXay4XDpArk9EGxOU6LXdq4vpyBsYwq+Xw="

# Function to create a JWT token
def create_jwt_token(data: dict, expires_delta: int = 60):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_delta)
    data["exp"] = expiration
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return token

# Function to verify a JWT token
def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_data
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/token")
def generate_token():
    token = create_jwt_token({"sub": "Daffa"})
    return {"token": token}

@app.get("/protected")
def protected_route(token: str):
    user_data = verify_jwt_token(token)
    return {"message": f"Hello, {user_data['sub']}! You have access to this route."}
