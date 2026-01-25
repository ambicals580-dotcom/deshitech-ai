from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def detect_intent(msg):
    msg = msg.lower()

    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "greeting"
    if "who are you" in msg:
        return "identity"
    if "remember" in msg:
        return "memory"
    if "help" in msg:
        return "help"
    return "general"

def generate_reply(intent, user_msg, memory):
    if intent == "greeting":
        return "Hello! I am DESHITECH AI 🇮🇳. How can I help you?"

    if intent == "identity":
        return "I am DESHITECH AI — Bharat ki buddhi aur takneek ki shakti."

    if intent == "memory":
        if not memory:
            return "I don’t remember anything yet."
        last = memory[-1]
        return f"I remember you said: '{last['user']}'"

    if intent == "help":
        return (
            "You can ask me questions, talk normally, or ask what I remember."
        )

    # General thinking
    return (
        f"You said: '{user_msg}'. "
        f"I am thinking and learning step by step."
    )

@app.get("/")
def home():
    return {"status": "DESHITECH AI running"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")

    memory = load_memory()

    intent = detect_intent(user_msg)
    reply = generate_reply(intent, user_msg, memory)

    memory.append({
        "user": user_msg,
        "ai": reply,
        "intent": intent
    })

    save_memory(memory)

    return {
        "reply": reply,
        "intent": intent,
        "memory_count": len(memory)
    }