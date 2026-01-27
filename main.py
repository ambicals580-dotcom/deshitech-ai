from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI(title="DESHITECH AI")

MEMORY_FILE = "memory.json"

# ---------------- MEMORY ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(data, limit=50):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data[-limit:], f, indent=2)

# ---------------- GENERATORS ----------------
def code_generator(msg):
    if "html" in msg:
        return """HTML Example:
```html
<!DOCTYPE html>
<html>
<body>
<h1>Hello DESHITECH AI</h1>
</body>
</html>
```"""
    if "python" in msg:
        return """Python Example:
```python
def greet(name):
    return f"Hello {name}"
print(greet("India"))
```"""
    return "Tell me what code you want (HTML / Python)."

def guide_generator(msg):
    return f"""Step-by-step guide for: {msg}

1. Understand the problem
2. Choose tools
3. Build small
4. Test
5. Improve
"""

def image_prompt_generator(msg):
    return f"""AI Image Prompt:
"A high quality {msg}, ultra realistic, professional lighting, clean background, 4K"
"""

def video_prompt_generator(msg):
    return f"""Video Plan for: {msg}

Scene 1: Hook (3s)
Scene 2: Problem
Scene 3: Solution
Scene 4: CTA
"""

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    msg = data.get("message", "").lower()

    memory = load_memory()
    memory.append({"user": msg})

    if "your name" in msg or "who are you" in msg:
        reply = "I am DESHITECH AI 🇮🇳, created by VISHIST AMBASTHA."
    elif any(w in msg for w in ["code", "html", "python"]):
        reply = code_generator(msg)
    elif any(w in msg for w in ["guide", "steps", "how"]):
        reply = guide_generator(msg)
    elif any(w in msg for w in ["image", "logo", "design"]):
        reply = image_prompt_generator(msg)
    elif any(w in msg for w in ["video", "reel", "short"]):
        reply = video_prompt_generator(msg)
    else:
        reply = "Ask me for code, guides, image ideas, or video plans."

    memory.append({"ai": reply})
    save_memory(memory)

    return {"reply": reply}