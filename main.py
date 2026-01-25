from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI(title="DESHITECH AI 🇮🇳")

MEMORY_FILE = "memory.json"

# ---------- MEMORY ----------
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

# ---------- AI LOGIC ----------
def deshitech_ai(message: str):
    msg = message.lower()

    if any(k in msg for k in ["html", "login"]):
        return """Here is a simple HTML login page:

```html
<!DOCTYPE html>
<html>
<body>
<h2>Login</h2>
<input placeholder="Username"><br><br>
<input type="password" placeholder="Password"><br><br>
<button>Login</button>
</body>
</html>
```"""

    if "python" in msg:
        return """Python example:

```python
def greet(name):
    return f"Hello {name}"

print(greet("DESHITECH"))
```"""

    if any(k in msg for k in ["image", "logo", "design"]):
        return (
            'AI Image Prompt:\n'
            '"A modern tech logo, professional, clean background, '
            '4k quality, futuristic, minimal design"'
        )

    if any(k in msg for k in ["video", "reel", "short"]):
        return (
            "Video Creation Guide:\n"
            "1. Hook (first 3 seconds)\n"
            "2. Problem\n"
            "3. Solution\n"
            "4. Call to Action"
        )

    if any(k in msg for k in ["guide", "how", "steps"]):
        return (
            "Step-by-step guide:\n"
            "1. Understand the requirement\n"
            "2. Break into small parts\n"
            "3. Build one by one\n"
            "4. Test\n"
            "5. Improve"
        )

    return "🇮🇳 DESHITECH AI ready. Ask for code, images, videos, or guidance."

# ---------- ROUTES ----------
@app.get("/", response_class=HTMLResponse)
def home():
    if os.path.exists("index.html"):
        return open("index.html").read()
    return "<h1>DESHITECH AI backend running</h1>"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    memory = load_memory()
    memory.append({"user": message})

    reply = deshitech_ai(message)

    memory.append({"ai": reply})
    save_memory(memory)

    return {"reply": reply}