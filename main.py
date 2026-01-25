from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "DESHITECH AI running"}

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower()

    # simple brain (logic layer)
    if "hello" in user_msg:
        reply = "Hello SIR 👋 I am RAM, your AI assistant."
    elif "who are you" in user_msg:
        reply = "I am RAM, designed by Ambicals – A Tech Group."
    else:
        reply = f"You said: {req.message}"

    return {"reply": reply}