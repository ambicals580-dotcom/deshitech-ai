from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DESHITECH AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Chat(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "name": "DESHITECH AI",
        "owner": "VISHIST AMBASTHA",
        "status": "running"
    }

@app.post("/chat")
def chat(data: Chat):
    msg = data.message.lower()

    if "hello" in msg:
        reply = "Hello, I am DESHITECH AI."
    elif "who are you" in msg:
        reply = "I am DESHITECH AI, created by VISHIST AMBASTHA."
    else:
        reply = f"You said: {data.message}"

    return {"reply": reply}
