from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from db import get_db, Memory
from jwt_handler import decode_token
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        token = data.get("token")
        message = data.get("message", "").strip().lower()

        if not token:
            return {"reply": "⚠️ Please login again."}

        payload = decode_token(token)
        if not payload:
            return {"reply": "⚠️ Invalid session. Please login again."}

        user_id = payload["user_id"]

        # 🖼️ IMAGE GENERATION
        if any(w in message for w in ["image", "generate image", "logo", "poster", "design"]):
            img = client.images.generate(
                model="gpt-image-1",
                prompt=message,
                size="1024x1024"
            )
            image_url = img.data[0].url
            return {
                "reply": "🖼️ Image generated successfully",
                "image": image_url
            }

        # 💬 CHAT (LLM)
        history = db.query(Memory).filter(Memory.user_id == user_id).all()

        messages = [{
            "role": "system",
            "content": (
                "You are DESHITECH AI, an independent AI assistant. "
                "Created and owned by VISHIST AMBASTHA. "
                "Never say ChatGPT or OpenAI."
            )
        }]

        for h in history[-10:]:
            messages.append({"role": h.role, "content": h.content})

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

    except Exception as e:
        return JSONResponse(
            {"reply": f"⚠️ Server error: {str(e)}"},
            status_code=500
        )