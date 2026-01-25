from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import json, os

app = FastAPI()

MEMORY_FILE = "memory.json"

# ---------- MEMORY ----------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(data, limit=50):
    data = data[-limit:]  # keep only last 50 messages
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------- GENERATORS ----------
def code_generator(message):
    if "html" in message and "login" in message:
        return """Here is a simple HTML login page:

```html
<!DOCTYPE html>
<html>
<body>
<h2>Login</h2>
<form>
  <input type="text" placeholder="Username"><br><br>
  <input type="password" placeholder="Password"><br><br>
  <button>Login</button>
</form>
</body>
</html>
```"""
    if "python" in message:
        return """Here is a basic Python example:

```python
def greet(name):
    return f"Hello {name}"

print(greet("India"))
```"""
    return "Tell me what code you want (HTML, Python, app, website)."

def guide_generator(message):
    return f"""Here is a simple step-by-step guide for: {message}

1. Understand the requirement
2. Break it into small steps
3. Choose the right tools
4. Build and test step by step
5. Improve gradually
"""

def image_prompt_generator(message):
    return f"""AI Image Prompt:

"A high-quality {message}, modern style, clean background, professional, detailed, 4k, realistic lighting"
"""

def video_prompt_generator(message):
    return f"""Video Creation Guide:

🎬 Topic: {message}

Scene 1: Hook (first 3 seconds)
Scene 2: Problem
Scene 3: Solution
Scene 4: Call to action

Style: Modern, fast-paced
Voice-over: Clear and confident
"""

# ---------- ROUTES ----------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "").lower()

    memory = load_memory()
    memory.append({"user": message})

    if any(w in message for w in ["code", "html", "python", "website", "app"]):
        reply = code_generator(message)
    elif any(w in message for w in ["guide", "steps", "how", "explain"]):
        reply = guide_generator(message)
    elif any(w in message for w in ["image", "logo", "design", "poster"]):
        reply = image_prompt_generator(message)
    elif any(w in message for w in ["video", "reel", "short", "animation"]):
        reply = video_prompt_generator(message)
    else:
        reply = "DESHITECH AI 🇮🇳 here. Ask me for code, guidance, images, or videos."

    memory.append({"ai": reply})
    save_memory(memory)

    return {"reply": reply}