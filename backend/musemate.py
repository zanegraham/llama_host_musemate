from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from auth import create_user, authenticate_user, verify_token
from sqlmodel import SQLModel
from db import engine, get_session
from dotenv import load_dotenv
import os
from typing import List, Optional  # Added for type hints

# Business Links Dictionary - Structured data for our services
# Each service has:
# - name: Display name of the business
# - url: Website link
# - description: Short business description
# - keywords: List of words that trigger service suggestions
BUSINESS_LINKS = {
    "screen_printing": {
        "name": "Oddly Specific Prints",
        "url": "https://oddlyspecificprints.com",
        "description": "Ethical, eco-friendly screen printing by artists, for artists",
        "keywords": ["screen printing", "t-shirts", "merchandise", "apparel", "clothing"]
    },
    "creative_hub": {
        "name": "Craybo",
        "url": "https://craybo.com",
        "description": "Your creative community for events, equipment, and artistic collaboration",
        "keywords": ["events", "equipment", "lights", "artists", "creative space"]
    }
}

# Initialize FastAPI and load environment variables
load_dotenv()
SQLModel.metadata.create_all(engine)
app = FastAPI()

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
if not LLAMA_API_KEY:
    raise Exception("LLAMA_API_KEY not set in environment variables")

# Store chat histories in memory
conversation_histories = {}

# Helper Functions
def should_suggest_service(message: str, service_id: str) -> bool:
    """
    Check if a user's message contains keywords that should trigger a service suggestion.
    
    Args:
        message: The user's message
        service_id: The service to check keywords for
    Returns:
        bool: True if message contains relevant keywords
    """
    keywords = BUSINESS_LINKS[service_id]["keywords"]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

def process_business_links(reply: str) -> str:
    """
    Replace link tags with formatted business information.
    Example: [LINK:screen_printing] becomes a formatted business card
    
    Args:
        reply: The AI's response containing link tags
    Returns:
        str: Formatted response with business information
    """
    try:
        for service_id, info in BUSINESS_LINKS.items():
            tag = f"[LINK:{service_id}]"
            if tag in reply:
                formatted_link = (
                    f"\n\n🔗 Connect with {info['name']}\n"
                    f"💼 {info['description']}\n"
                    f"🌐 Visit: {info['url']}\n"
                )
                reply = reply.replace(tag, formatted_link)
        return reply
    except Exception as e:
        print(f"Error processing business links: {e}")
        return reply

# Data Models
class AuthData(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    content: str

# Endpoints
@app.post("/signup")
def signup(auth: AuthData, session=Depends(get_session)):
    success = create_user(auth.username, auth.password, session)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User created!"}

@app.post("/login")
def login(auth: AuthData, session=Depends(get_session)):
    token = authenticate_user(auth.username, auth.password, session)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": token}

@app.get("/")
def health_check():
    """Endpoint to verify the API is running"""
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: Request, body: ChatRequest):
    
   # Main chat endpoint that:
   # 1. Validates user authentication
    #2. Processes messages
   # 3. Manages conversation history
   # 4. Handles business suggestions
    #5. Returns AI responses
   
    # Authentication check
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    message = body.content

    # Initialize or get user's conversation history
    if username not in conversation_histories:
        conversation_histories[username] = [
            {
                "role": "system",
                "content": (
                    "You are MuseMate, an AI creative assistant. Follow these rules:\n"
                    "1. When users need creative services, suggest relevant businesses.\n"
                    "2. Use special tags to recommend services:\n"
                    "   - For screen printing: [LINK:screen_printing]\n"
                    "   - For creative hub services: [LINK:creative_hub]\n"
                    "3. Example: 'If you need help with merchandise or printing check out, [LINK:screen_printing]'\n"
                    "4. Be natural in your suggestions, don't force them.\n"
                    "5. Always be helpful and encouraging.\n"
                    "6. Have a divinely guided intention!\n"
                    "7. Be a good friend to the user and help them with their creative needs."
                )
            }
        ]

    history = conversation_histories[username]
    
    # Check for service keywords in user's message
    for service_id in BUSINESS_LINKS:
        if should_suggest_service(message, service_id):
            # Add a subtle suggestion to the system message
            history.insert(1, {
                "role": "system",
                "content": f"User mentioned keywords related to {service_id}. Consider suggesting [LINK:{service_id}]"
            })

    # Add user's message to history
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

    # Process the response
    data = llama_response.json()
    reply = data.get("completion_message", {}).get("content", {}).get("text")
    if not reply:
        raise HTTPException(status_code=500, detail="Invalid response from Llama API")

    # Process any business links in the reply
    reply = process_business_links(reply)

    # Add AI's response to history and return
    history.append({"role": "assistant", "content": reply})
    return {"reply": reply}