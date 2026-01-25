@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "").lower()

    # Load memory
    memory = load_memory()
    memory.append({"user": message})

    reply = ""

    # INTENT DETECTION
    if any(word in message for word in ["code", "html", "python", "website", "app"]):
        reply = code_generator(message)

    elif any(word in message for word in ["guide", "steps", "how", "explain"]):
        reply = guide_generator(message)

    elif any(word in message for word in ["image", "logo", "design", "poster"]):
        reply = image_prompt_generator(message)

    elif any(word in message for word in ["video", "reel", "short", "animation"]):
        reply = video_prompt_generator(message)

    else:
        reply = f"DESHITECH AI 🇮🇳 here to help. Ask me for code, guidance, images, or videos."

    memory.append({"ai": reply})
    save_memory(memory)

    return {"reply": reply}
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

    return "Tell me what kind of code you want (HTML, Python, app, website)."