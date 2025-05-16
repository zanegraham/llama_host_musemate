# backend/auth.py
import jwt
import time
from passlib.hash import bcrypt

SECRET_KEY = "super-secret-key"  # Change this in prod

fake_users_db = {}

def create_user(username: str, password: str):
    if username in fake_users_db:
        return False
    hashed_pw = bcrypt.hash(password)
    fake_users_db[username] = {"password": hashed_pw}
    return True

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not bcrypt.verify(password, user["password"]):
        return None
    return generate_token(username)

def generate_token(username: str):
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
