from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os, json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="DESHITECH AI")

MEMORY_FILE = "memory.json"
MAX_MEMORY = 20

# ---------- MEMORY ----------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem[-MAX_MEMORY:], f, indent=2)

# ---------- ROUTES ----------
@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    user_msg = data.get("message", "")

    memory = load_memory()

    system_prompt = (
        "You are DESHITECH AI, an independent Indian AI assistant. "
        "You are NOT ChatGPT. You are created and owned by VISHIST AMBASTHA. "
        "Never mention OpenAI or ChatGPT. Be helpful, clear, and concise."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for m in memory:
        messages.append(m)
    messages.append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    memory.append({"role": "user", "content": user_msg})
    memory.append({"role": "assistant", "content": reply})
    save_memory(memory)

    return {"reply": reply}

@app.post("/image")
async def image(req: Request):
    prompt = (await req.json()).get("prompt", "")

    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    return {"image_url": img.data[0].url}