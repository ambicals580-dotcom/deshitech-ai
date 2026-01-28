from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from database import SessionLocal, User, Memory
from auth import hash_password, authenticate

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="DESHITECH AI")

# ---------- DB ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- ROUTES ----------
@app.get("/", response_class=HTMLResponse)
def login_page():
    return open("login.html").read()

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate(db, email, password)
    if not user:
        return HTMLResponse("Invalid login", status_code=401)
    return RedirectResponse(f"/chat-ui?user_id={user.id}", status_code=302)

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui():
    return open("index.html").read()

@app.post("/chat")
async def chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user_id = data["user_id"]
    message = data["message"]

    memories = db.query(Memory).filter(Memory.user_id == user_id).all()
    messages = [{
        "role": "system",
        "content": "You are DESHITECH AI, created by VISHIST AMBASTHA. Never mention OpenAI or ChatGPT."
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