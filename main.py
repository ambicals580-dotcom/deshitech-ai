import os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

---------- CONFIG ----------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MEMORY_FILE = "memory.json"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

---------- MEMORY ----------

def load_memory():
if os.path.exists(MEMORY_FILE):
with open(MEMORY_FILE, "r") as f:
return json.load(f)
return []

def save_memory(data, limit=100):
with open(MEMORY_FILE, "w") as f:
json.dump(data[-limit:], f, indent=2)

---------- HOME ----------

@app.get("/", response_class=HTMLResponse)
def home():
return """

<!DOCTYPE html>  <html>  
<head>  
<title>DESHITECH AI</title>  
<style>  
body{margin:0;background:#020617;color:white;font-family:Arial}  
header{display:flex;align-items:center;padding:15px;border-bottom:1px solid #1e293b}  
header img{height:40px;margin-right:10px}  
main{padding:20px}  
input{width:80%;padding:14px;border-radius:8px;border:none}  
button{padding:14px 20px;background:#22c55e;border:none;border-radius:8px;cursor:pointer}  
pre{margin-top:15px;white-space:pre-wrap}  
</style>  
</head>  
<body>  <header>  
<img src="/static/logo.png">  
<h2>DESHITECH AI 🇮🇳</h2>  
</header>  <main>  
<h3>Ask me anything</h3>  
<input id="msg" placeholder="Code, image idea, video idea, guidance...">  
<button onclick="send()">Send</button>  
<pre id="out"></pre>  
</main>  <script>  
async function send(){  
 let m=document.getElementById("msg").value;  
 let r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:m})});  
 let d=await r.json();  
 document.getElementById("out").innerText=d.reply;  
}  
</script>  </body>  
</html>  
"""  ---------- CHAT ----------

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

Please give me code with better ui and login panel