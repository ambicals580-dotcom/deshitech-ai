import os, json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

# ---------- CONFIG ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MEMORY_FILE = "memory.json"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple user credentials for demo
USERS = {
    "admin": "password123",
    "user": "userpass"
}

# ---------- MEMORY ----------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(data, limit=100):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data[-limit:], f, indent=2)

# ---------- LOGIN ----------
@app.get("/", response_class=HTMLResponse)
def login_page():
    return """
<!DOCTYPE html>
<html>
<head>
<title>DESHITECH AI Login</title>
<style>
body { margin:0; font-family:Arial; background:#0f172a; color:white; display:flex; justify-content:center; align-items:center; height:100vh;}
form { background:#1e293b; padding:40px; border-radius:12px; display:flex; flex-direction:column; width:300px; }
input { margin-bottom:20px; padding:12px; border-radius:6px; border:none; }
button { padding:12px; border:none; border-radius:6px; background:#22c55e; color:white; cursor:pointer; font-weight:bold;}
h2 { text-align:center; margin-bottom:20px;}
</style>
</head>
<body>
<form method="POST" action="/login">
<h2>DESHITECH AI Login</h2>
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
</body>
</html>
"""

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        response = RedirectResponse(url="/chat_ui", status_code=303)
        response.set_cookie(key="user", value=username)
        return response
    return HTMLResponse("<h2>Invalid credentials! Go back and try again.</h2>")

# ---------- CHAT UI ----------
@app.get("/chat_ui", response_class=HTMLResponse)
def chat_ui(user: str = ""):
    return """
<!DOCTYPE html>
<html>
<head>
<title>DESHITECH AI Chat</title>
<style>
body { margin:0; font-family:Arial; background:#020617; color:white; }
header { display:flex; align-items:center; padding:15px; border-bottom:1px solid #1e293b; background:#111827; }
header img { height:40px; margin-right:10px; }
main { padding:20px; max-width:800px; margin:auto; }
#chat { height:400px; overflow-y:auto; border:1px solid #334155; padding:10px; border-radius:8px; margin-bottom:20px; background:#0f172a; }
input { width:75%; padding:14px; border-radius:8px; border:none; margin-right:10px; }
button { padding:14px 20px; background:#22c55e; border:none; border-radius:8px; cursor:pointer; }
.message { margin-bottom:10px; }
.user { color:#22c55e; }
.assistant { color:#60a5fa; }
</style>
</head>
<body>

<header>
<img src="/static/logo.png">
<h2>DESHITECH AI 🇮🇳</h2>
</header>

<main>
<h3>Welcome, """ + "{user}" + """!</h3>
<div id="chat"></div>
<input id="msg" placeholder="Ask me anything...">
<button onclick="send()">Send</button>
</main>

<script>
async function send(){
    let msg=document.getElementById("msg").value;
    if(!msg) return;
    let chat=document.getElementById("chat");
    chat.innerHTML += `<div class="message user">You: ${msg}</div>`;
    document.getElementById("msg").value="";
    let r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg})});
    let d=await r.json();
    chat.innerHTML += `<div class="message assistant">AI: ${d.reply}</div>`;
    chat.scrollTop = chat.scrollHeight;
}
</script>

</body>
</html>
"""

# ---------- CHAT ----------
@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    user_msg = data.get("message","")

    memory = load_memory()
    memory.append({"role":"user","content":user_msg})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory
    )

    reply = response.choices[0].message.content
    memory.append({"role":"assistant","content":reply})
    save_memory(memory)

    return {"reply": reply}