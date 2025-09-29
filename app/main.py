from fastapi import FastAPI
from app.routes import router  # import the chat routes

app = FastAPI(
    title="Travel Assistant",
    description="Travel Assistant: Chatbot",
    version="1.0"
)

# Include routes
app.include_router(router)

# Optional: simple root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Travel Assistant. Please enable geolocation to chat."}
