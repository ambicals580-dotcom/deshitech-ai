import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from openai import OpenAI

from db import get_db, ChatMemory
from jwt_handler import create_token, verify_token

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

SYSTEM_PROMPT = (
    "You are DESHITECH AI. "
    "Owner: VISHIST AMBASTHA. "
    "Never say ChatGPT or OpenAI."
)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# -------- LOGIN --------
@app.post("/login")
async def login(req: Request):
    data = await req.json()
    username = data.get("username")
    if not username:
        return {"error": "Username required"}
    token = create_token(username)
    return {"token": token}

# -------- CHAT --------
@app.post("/chat")
async def chat(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    token = data.get("token")
    message = data.get("message")

    user = verify_token(token)
    if not user:
        return {"reply": "⚠️ Invalid session. Please login again."}

    # IMAGE
    if any(w in message.lower() for w in ["image", "logo", "poster", "design"]):
        img = client.images.generate(
            model="gpt-image-1",
            prompt=message,
            size="1024x1024"
        )
        return {"image": img.data[0].url}

    # MEMORY SAVE
    db.add(ChatMemory(user=user, role="user", content=message))
    db.commit()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )

    reply = response.choices[0].message.content
    db.add(ChatMemory(user=user, role="ai", content=reply))
    db.commit()

    return {"reply": reply}