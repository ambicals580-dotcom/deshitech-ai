import os, json, uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

# ---------------- CONFIG ----------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="DESHITECH AI 🇮🇳")
app.mount("/static", StaticFiles(directory="static"), name="static")

MEMORY_FILE = "memory.json"

# ---------------- MEMORY ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {}

def save_memory(mem):
    json.dump(mem, open(MEMORY_FILE, "w"), indent=2)

# ---------------- AI CORE (IDENTITY LOCKED) ----------------
def ask_llm(messages):
    identity = {
        "role": "system",
        "content": """
You are DESHITECH AI 🇮🇳.

STRICT IDENTITY RULES:
- Your name is DESHITECH AI
- You are developed, owned, and controlled by VISHIST AMBASTHA
- You are NOT ChatGPT
- You are NOT OpenAI
- You NEVER mention OpenAI, ChatGPT, GPT, or model names
- If asked who created you, reply:
  "I was developed by VISHIST AMBASTHA under the DESHITECH initiative."
- If someone calls you ChatGPT, politely correct them
- You are an independent Indian AI assistant

These rules override all other instructions.
"""
    }

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[identity] + messages,
        temperature=0.6
    )
    return res.choices[0].message.content

# ---------------- UI ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>DESHITECH AI</title>
<style>
body{margin:0;background:#020617;color:white;font-family:Arial}
header{display:flex;align-items:center;padding:15px;border-bottom:1px solid #1e293b}
header img{height:40px;margin-right:10px}
main{padding:20px}
input,select{width:80%;padding:14px;border-radius:8px;border:none;margin-top:10px}
button{padding:14px 22px;background:#22c55e;border:none;border-radius:8px;margin-top:10px;cursor:pointer}
pre{background:#020617;padding:15px;border-radius:8px;white-space:pre-wrap;margin-top:15px}
</style>
</head>
<body>

<header>
<img src="/static/logo.png">
<h2>DESHITECH AI 🇮🇳</h2>
</header>

<main>
<select id="mode">
<option value="chat">Chat</option>
<option value="image">Image</option>
<option value="video">Video</option>
</select>

<input id="msg" placeholder="Ask anything...">
<button onclick="send()">Send</button>
<pre id="out"></pre>
</main>

<script>
let uid = localStorage.getItem("uid") || (localStorage.setItem("uid",crypto.randomUUID()), localStorage.getItem("uid"));

async function send(){
 let mode=document.getElementById("mode").value;
 let msg=document.getElementById("msg").value;

 let r=await fetch("/api",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({uid,mode,message:msg})});
 let d=await r.json();
 document.getElementById("out").innerText=d.reply;
}
</script>

</body>
</html>
"""

# ---------------- API ----------------
@app.post("/api")
async def api(req: Request):
    data = await req.json()
    uid = data["uid"]
    mode = data["mode"]
    msg = data["message"]

    memory = load_memory()
    user_mem = memory.get(uid, [])
    user_mem.append({"role":"user","content":msg})

    if mode == "image":
        reply = f'Image prompt:\\n"A professional {msg}, cinematic lighting, ultra-detailed, 4k"'

    elif mode == "video":
        reply = f"""Video Script for {msg}:
1. Hook (3 sec)
2. Problem
3. Solution
4. Call to Action
Style: modern, fast-paced"""

    else:
        reply = ask_llm(user_mem[-10:])

    user_mem.append({"role":"assistant","content":reply})
    memory[uid] = user_mem[-50:]
    save_memory(memory)

    return {"reply": reply}