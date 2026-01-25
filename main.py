from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import openai
import os
import json

app = FastAPI()

# Load OpenAI key from Render environment
openai.api_key = os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "memory.json"

# ---------------- MEMORY ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(memory, limit=30):
    memory = memory[-limit:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# ---------------- AI CORE ----------------
def ask_llm(message, memory):
    messages = [
        {"role": "system", "content": "You are DESHITECH AI 🇮🇳 — intelligent, helpful, expert in code, images, videos, and guidance."}
    ]

    for m in memory:
        messages.append(m)

    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6
    )

    return response.choices[0].message.content

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>DESHITECH AI</title>
        <style>
            body{background:#0f172a;color:white;font-family:Arial;text-align:center}
            input{width:70%;padding:12px;border-radius:6px}
            button{padding:12px 20px;margin-top:10px;background:#22c55e;border:none;border-radius:6px}
        </style>
    </head>
    <body>
        <h1>DESHITECH AI 🇮🇳</h1>
        <p>India's Intelligence, Powered by AI</p>
        <input id="msg" placeholder="Ask anything...">
        <br>
        <button onclick="send()">Send</button>
        <pre id="out"></pre>

        <script>
        async function send(){
            let m = document.getElementById("msg").value;
            let r = await fetch("/chat", {
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({message:m})
            });
            let d = await r.json();
            document.getElementById("out").innerText = d.reply;
        }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    user_message = data.get("message")

    memory = load_memory()
    memory.append({"role": "user", "content": user_message})

    reply = ask_llm(user_message, memory)

    memory.append({"role": "assistant", "content": reply})
    save_memory(memory)

    return {"reply": reply}