from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from auth import create_user, authenticate_user, verify_token
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

app = FastAPI()

# CORS settings — adjust origin for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
if not LLAMA_API_KEY:
    raise Exception("LLAMA_API_KEY not set in environment variables")

# Memory per user (swap with DB later)
conversation_histories = {}

# -------------------------------
# Auth System
# -------------------------------

class AuthData(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(auth: AuthData):
    success = create_user(auth.username, auth.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User created!"}

@app.post("/login")
def login(auth: AuthData):
    token = authenticate_user(auth.username, auth.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": token}

# -------------------------------
# Chat Endpoint
# -------------------------------

class ChatRequest(BaseModel):
    content: str

@app.post("/chat")
async def chat(request: Request, body: ChatRequest):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    message = body.content

    # Initialize user-specific history
    if username not in conversation_histories:
        conversation_histories[username] = [
            {
                "role": "system",
                "content": (
                    "You are MuseMate, an AI that helps with brainstorming creative ideas, "
                    "projects, and turning dreams into plans. Be kind, clear, and inspiring."
                )
            }
        ]

    history = conversation_histories[username]
    history.append({"role": "user", "content": message})

    # Call Llama API
    try:
        llama_response = requests.post(
            "https://api.llama.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {LLAMA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": history
            }
        )
        llama_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Llama API error: {e} {llama_response.text if 'llama_response' in locals() else ''}")
        raise HTTPException(status_code=500, detail="Llama API failed")

    data = llama_response.json()
    # Adjust this depending on actual Llama API response structure
    reply = data.get("completion_message", {}).get("content", {}).get("text")
    if not reply:
        raise HTTPException(status_code=500, detail="Invalid response from Llama API")

    history.append({"role": "assistant", "content": reply})

    return {"reply": reply}
