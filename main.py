import os, json, sqlite3, hashlib
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

# -------- CONFIG --------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="DESHITECH AI 🇮🇳")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------- DATABASE --------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
conn.commit()

# -------- MEMORY --------
def load_memory(user):
    if os.path.exists("memory.json"):
        mem=json.load(open("memory.json"))
        return mem.get(user,[])
    return []

def save_memory(user,data):
    mem={}
    if os.path.exists("memory.json"):
        mem=json.load(open("memory.json"))
    mem[user]=data[-30:]
    json.dump(mem,open("memory.json","w"),indent=2)

# -------- SECURITY --------
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# -------- AI --------
def ask_llm(messages):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6
    )
    return res.choices[0].message.content

# -------- UI TEMPLATES --------
login_page = """
<h2>DESHITECH AI Login</h2>
<form method="post">
<input name="username" placeholder="Username"><br><br>
<input name="password" type="password" placeholder="Password"><br><br>
<button>Login</button>
</form>
<a href="/signup">Create account</a>
"""

signup_page = """
<h2>DESHITECH AI Signup</h2>
<form method="post">
<input name="username" placeholder="Username"><br><br>
<input name="password" type="password" placeholder="Password"><br><br>
<button>Signup</button>
</form>
<a href="/login">Login</a>
"""

chat_page = """
<!DOCTYPE html>
<html>
<head>
<title>DESHITECH AI</title>
</head>
<body style="background:#020617;color:white;text-align:center;font-family:Arial">

<img src="/static/logo.png" height="60"><br>
<h2>DESHITECH AI 🇮🇳</h2>
<p>Welcome {user}</p>

<select id="mode">
<option>chat</option>
<option>image</option>
<option>video</option>
</select><br><br>

<input id="msg" style="width:60%;padding:10px"><br><br>
<button onclick="send()">Send</button>
<pre id="out"></pre>

<br><br>
<a href="/logout" style="color:red">Logout</a>

<script>
async function send(){
 let m=document.getElementById("msg").value;
 let mode=document.getElementById("mode").value;
 let r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:m,mode:mode})});
 let d=await r.json();
 document.getElementById("out").innerText=d.reply;
}
</script>

</body>
</html>
"""

# -------- SESSION MEMORY --------
sessions = {}

# -------- ROUTES --------
@app.get("/")
def home():
    return RedirectResponse("/login")

@app.get("/login", response_class=HTMLResponse)
def login():
    return login_page

@app.post("/login")
def do_login(username:str=Form(...), password:str=Form(...)):
    pw = hash_pass(password)
    r=c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,pw)).fetchone()
    if r:
        sid = hash_pass(username+pw)
        sessions[sid]=username
        res=RedirectResponse("/chatui")
        res.set_cookie("session",sid)
        return res
    return "Invalid login"

@app.get("/signup", response_class=HTMLResponse)
def signup():
    return signup_page

@app.post("/signup")
def do_signup(username:str=Form(...), password:str=Form(...)):
    try:
        c.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,hash_pass(password)))
        conn.commit()
        return RedirectResponse("/login")
    except:
        return "Username exists"

@app.get("/chatui", response_class=HTMLResponse)
def chatui(req: Request):
    sid=req.cookies.get("session")
    if sid not in sessions:
        return RedirectResponse("/login")
    return chat_page.replace("{user}",sessions[sid])

@app.get("/logout")
def logout(req: Request):
    sid=req.cookies.get("session")
    sessions.pop(sid,None)
    res=RedirectResponse("/login")
    res.delete_cookie("session")
    return res

@app.post("/chat")
async def chat(req: Request):
    sid=req.cookies.get("session")
    if sid not in sessions:
        return {"reply":"Login first"}

    user=sessions[sid]
    data=await req.json()
    msg=data["message"]
    mode=data["mode"]

    mem=load_memory(user)
    mem.append({"role":"user","content":msg})

    if mode=="image":
        reply=f'Image prompt: "{msg}, cinematic, ultra realistic"'
    elif mode=="video":
        reply=f"Video script: Hook → Problem → Solution → CTA for {msg}"
    else:
        system={"role":"system","content":"You are DESHITECH AI 🇮🇳"}
        reply=ask_llm([system]+mem[-8:])

    mem.append({"role":"assistant","content":reply})
    save_memory(user,mem)

    return {"reply":reply}