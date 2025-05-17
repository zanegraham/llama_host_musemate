from passlib.hash import bcrypt
from models import User
import jwt
import os
import datetime

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

def create_user(username: str, password: str, session):
    if session.query(User).filter_by(username=username).first():
        return False
    user = User(username=username, password_hash=bcrypt.hash(password))
    session.add(user)
    session.commit()
    return True

def authenticate_user(username: str, password: str, session):
    user = session.query(User).filter_by(username=username).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return None
    return generate_token(username)  # Generate JWT token if authentication succeeds

def generate_token(username: str):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("username")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None