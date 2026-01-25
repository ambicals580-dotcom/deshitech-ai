from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "DESHITECH AI is running 🇮🇳"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()

        if not message:
            return JSONResponse(status_code=400, content={"error": "Empty message"})

        reply = f"DESHITECH AI 🇮🇳 says: {message}"

        return {"reply": reply}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})