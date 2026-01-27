from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>DESHITECH AI is running ✅</h1>"

@app.get("/health")
def health():
    return {"status": "ok"}