# test_basic.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Basic Travel Assistant Test")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
      <head>
        <title>Basic Test</title>
      </head>
      <body>
        <h1>🚀 Travel Assistant Test</h1>
        <p>Backend is running correctly.</p>
      </body>
    </html>
    """

@app.get("/ping")
async def ping():
    return {"message": "pong"}
