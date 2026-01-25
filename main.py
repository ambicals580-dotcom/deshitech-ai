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

@app.get("/")
def home():
    return {"status": "DESHITECH AI running"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")

    memory = load_memory()

    reply = f"You said: {user_msg}. I remember {len(memory)} things."

    memory.append({
        "user": user_msg,
        "ai": reply
    })

    save_memory(memory)

    return {
        "reply": reply,
        "memory_count": len(memory)
    } 