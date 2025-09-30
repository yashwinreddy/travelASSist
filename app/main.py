from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router  # Import the chat routes

# Create FastAPI instance
app = FastAPI(
    title="Travel Assistant",
    description="An AI-powered Travel Assistant chatbot",
    version="1.0.0"
)

# Enable CORS (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific domains later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "🚀 Welcome to the Travel Assistant API. Please enable geolocation to chat."
    }
