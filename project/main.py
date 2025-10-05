# main.py
from fastapi import FastAPI
from app.routes import router  # import routes from app/routes.py

app = FastAPI(
    title="Travel Assistant",
    description="Travel Assistant: Chatbot using location, routes, traffic, and weather info.",
    version="1.0"
)

# Include API routes
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to the Travel Assistant. Please enable geolocation to start chatting."
    }
