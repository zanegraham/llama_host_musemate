from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# Load your secret API key
load_dotenv()
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
if not LLAMA_API_KEY:
    raise ValueError("Missing LLAMA_API_KEY in .env file")

# Set up your web app
app = FastAPI()

# Allow your frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend runs here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the format we expect when the frontend sends a message
class Message(BaseModel):
    content: str

# Start the chat history
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are MuseMate, an AI that helps with brainstorming creative ideas and connecting people "
            "through context, events, and inspiration. When users need help with screen printing, posters, "
            "merch, or apparel, guide them to Oddly Specific Prints. For event planning, artwork, development, "
            "or creative support, guide them to Craybo."
        )
    }
]

# Chat endpoint - the frontend will send a message here
@app.post("/chat")
async def chat(message: Message):
    # Add user message to history
    conversation_history.append({"role": "user", "content": message.content})

    # Send to Llama API
    response = requests.post(
        "https://api.llama.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {LLAMA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
            "messages": conversation_history
        }
    )

    # Return the reply
    if response.status_code == 200:
        reply = response.json()["completion_message"]["content"]["text"]
        conversation_history.append({"role": "assistant", "content": reply})
        return {"reply": reply}
    else:
        return {"error": response.text}
