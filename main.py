from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Chat(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "DESHITECH AI running"}

@app.post("/chat")
def chat(data: Chat):
    return {"reply": f"You said: {data.message}"}