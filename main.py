from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from database import SessionLocal, User, Memory
from auth import hash_password, verify_password
from jwt_handler import create_token, decode_token

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="DESHITECH AI")

# ---------- DB ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- PAGES ----------
@app.get("/", response_class=HTMLResponse)
def login_page():
    return open("login.html").read()

@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui():
    return open("index.html").read()

# ---------- AUTH ----------
@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    return {"message": "Registered successfully"}

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"user_id": user.id})
    return {"token": token}

# ---------- CHAT ----------
@app.post("/chat")
async def chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    token = data.get("token")
    message = data.get("message")

    payload = decode_token(token)
    user_id = payload["user_id"]

    memories = db.query(Memory).filter(Memory.user_id == user_id).all()

    messages = [{
        "role": "system",
        "content": "You are DESHITECH AI, created by VISHIST AMBASTHA. Never mention ChatGPT or OpenAI."
    }]

    for m in memories[-10:]:
        messages.append({"role": m.role, "content": m.content})

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = response.choices[0].message.content

    db.add(Memory(user_id=user_id, role="user", content=message))
    db.add(Memory(user_id=user_id, role="assistant", content=reply))
    db.commit()

    return {"reply": reply}