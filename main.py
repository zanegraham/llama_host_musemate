import os
import gradio as gr
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv

# SARAHS FITNESS AI !!!!!

# Load .env file (if you're using one)
load_dotenv()

# Get your API key from environment variable
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")

# This is to read the info from the pdf uploaded 
def extract_text_from_pdf(pdf_path, max_chars=4000):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        if len(text) + len(page_text) > max_chars:
            break
        text += page_text
    return text

pdf_path = "Sarah-HealthTips-Test.pdf"
pricing_text = extract_text_from_pdf(pdf_path)


# MAIN AI "FUNCTIONS" / VARIABLES
url = "https://api.llama.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {LLAMA_API_KEY}",
    "Content-Type": "application/json"
}

# KEEP TRACK OF CONVO HISTORY
conversation_history = [
    {
        "role": "system",
        "content": f"You are an assistant helping with screen printing orders. Use only the following pricing info to answer questions:\n\n{pricing_text}"
    }
]


# SENDING REQUEST TO LLAMA API
def get_ai_response():
    payload = {
        "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": conversation_history
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result["completion_message"]["content"]["text"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"
    
# TAKES TYPES QUESTION - TALKS TO AI - RETURNS CHAT LIST FOR DISPLAY
def ask_question(user_input, chat_history):
    # Add user's message to history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Get AI response
    ai_reply = get_ai_response()

    # Add AI reply to history
    conversation_history.append({"role": "assistant", "content": ai_reply})
    
    # Add to visible chat history in UI
    chat_history.append((user_input, ai_reply))
    
    return chat_history, chat_history
    
# STARTS / INITIATES THE INTERACTION /CONVO LOOP WITH AI
def chat_with_assistant(user_input, chat_history):
    return ask_question(user_input, chat_history)

# Create Gradio UI
ui = gr.Interface(
    fn=chat_with_assistant,
    inputs=[gr.Textbox(lines=2, placeholder="Ask about fitness..."), gr.State([])],
    outputs=[gr.Chatbot(), gr.State()],
    title="🏋️‍♀️ Sarah's Fitness Assistant",
    description="Ask about workouts, health info, and more based on Sarah's (TruFit Movements) guide!"
)

ui.launch(share=True)