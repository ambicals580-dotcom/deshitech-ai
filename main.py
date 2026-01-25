from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os, json

app = FastAPI(title="DESHITECH AI 🇮🇳")

MEMORY_FILE = "memory.json"

# ---------------- MEMORY ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(data, limit=100):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data[-limit:], f, indent=2)

# ---------------- CORE AI LOGIC ----------------
def deshitech_ai(message: str):
    msg = message.lower()

    if any(k in msg for k in ["html", "python", "code", "website", "app"]):
        return f"""
🧠 **DESHITECH AI – CODE MODE**

You asked: **{message}**

Example (HTML Login):

```html
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
</head>
<body>
<h2>Login</h2>
<input placeholder="Username"><br><br>
<input type="password" placeholder="Password"><br><br>
<button>Login</button>
</body>
</html>