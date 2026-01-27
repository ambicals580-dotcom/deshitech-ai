import os, json
from fastapi import FastAPI, Request, Form
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

# ---------------- LLM (IDENTITY LOCKED) ----------------
def ask_llm(messages):
    system = {
        "role": "system",
        "content": """
You are DESHITECH AI 🇮🇳.
Developed and owned by VISHIST AMBASTHA.
You are NOT ChatGPT and never mention OpenAI or GPT.
You help with coding, startups, guidance, and technology.
"""
    }

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system] + messages,
        temperature=0.6
    )
    return res.choices[0].message.content

# ---------------- LOGIN PAGE ----------------
@app.get("/", response_class=HTMLResponse)
def login():
    return """
<html>
<head><title>DESHITECH AI Login</title></head>
<body style="background:#020617;color:white;text-align:center;font-family:Arial">
<h2>DESHITECH AI 🇮🇳</h2>
<form action="/chat" method="post">
<input name="username" placeholder="Enter username" required style="padding:12px;width:60%"><br><br>
<button style="padding:12px 20px">Enter</button>
</form>
</body>
</html>
"""

# ---------------- CHAT UI ----------------
@app.post("/chat", response_class=HTMLResponse)
def chat_ui(username: str = Form(...)):
    return f"""
<html>
<head>
<title>DESHITECH AI</title>
<style>
body{{background:#020617;color:white;font-family:Arial}}
input,select,button{{padding:12px;margin-top:10px;width:80%}}
pre{{background:#020617;padding:15px;border:1px solid #1e293b}}
</style>
</head>
<body>
<img src="/static/logo.png" height="40">
<h3>Welcome {username}</h3>

<select id="mode">
<option value="chat">Chat</option>
<option value="image">Image</option>
</select><br>

<input id="msg" placeholder="Ask anything..."><br>
<button onclick="send()">Send</button>

<pre id="out"></pre>

<script>
async function send(){{
 let msg=document.getElementById("msg").value;
 let mode=document.getElementById("mode").value;

 let r=await fetch("/api",{{
 method:"POST",
 headers:{{"Content-Type":"application/json"}},
 body:JSON.stringify({{
   username:"{username}",
   mode:mode,
   message:msg
 }})
 }});

 let d=await r.json();
 document.getElementById("out").innerText=d.reply;
}}
</script>
</body>
</html>
"""

# ---------------- API ----------------
@app.post("/api")
async def api(req: Request):
    data = await req.json()
    user = data["username"]
    mode = data["mode"]
    msg = data["message"]

    memory = load_memory()
    chat = memory.get(user, [])
    chat.append({"role":"user","content":msg})

    if mode == "image":
        img = client.images.generate(
            model="gpt-image-1",
            prompt=msg,
            size="1024x1024"
        )
        reply = img.data[0].url

    else:
        reply = ask_llm(chat[-10:])

    chat.append({"role":"assistant","content":reply})
    memory[user] = chat[-50:]
    save_memory(memory)

    return {"reply": reply}