from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from database import SessionLocal, User, Memory
from auth import hash_password, verify_password
from jwt_handler import create_token, decode_token

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="DESHITECH AI")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def login_page():
    return open("login.html").read()

@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui():
    return open("index.html").read()

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    return {"ok": True}

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return JSONResponse({"error": "Invalid login"}, status_code=401)

    token = create_token({"user_id": user.id})
    return {"token": token}

@app.post("/chat")
async def chat(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        token = data.get("token")
        text = data.get("message")

        if not token:
            return {"reply": "⚠️ Login expired. Please login again."}

        payload = decode_token(token)
        if not payload:
            return {"reply": "⚠️ Invalid session. Please login again."}

        user_id = payload["user_id"]

        history = db.query(Memory).filter(Memory.user_id == user_id).all()

        messages = [{
            "role": "system",
            "content": (
                "You are DESHITECH AI, a private AI assistant. "
                "Created and owned by VISHIST AMBASTHA. "
                "Never say ChatGPT or OpenAI."
            )
        }]

        for h in history[-10:]:
            messages.append({"role": h.role, "content": h.content})

        messages.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content

        db.add(Memory(user_id=user_id, role="user", content=text))
        db.add(Memory(user_id=user_id, role="assistant", content=reply))
        db.commit()

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"⚠️ Internal error: {str(e)}"} 