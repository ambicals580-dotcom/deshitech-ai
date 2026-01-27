from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI()

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(data, limit=50):
    data = data[-limit:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

@app.get("/", response_class=HTMLResponse)
def home():
    if not os.path.exists("index.html"):
        return "<h1>index.html missing</h1>"
    with open("index.html", "r") as f:
        return f.read()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    memory = load_memory()
    memory.append({"user": message})

    reply = "DESHITECH AI 🇮🇳 — Owner: Ambicals"

    memory.append({"ai": reply})
    save_memory(memory)

    return {"reply": reply}