from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Chat(BaseModel):
    message: str

@app.get("/")
def root():
    return {
        "name": "DESHITECH AI",
        "status": "running"
    }

@app.post("/chat")
def chat(data: Chat):
    return {
        "reply": f"You said: {data.message}"
    }