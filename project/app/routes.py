# routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.cache_manager import CacheManager
from app.api_client import MapsClient, WeatherClient
from app.llm_client import LLMClient
import time
import uuid

router = APIRouter()

cache = CacheManager()
maps_client = MapsClient()
weather_client = WeatherClient()
llm_client = LLMClient()

@router.post("/chat")
async def chat_endpoint(request: Request):
    """
    Receives: {user_id, query, lat, lng, timestamp}
    Returns: {text, snapshot_id}
    """
    data = await request.json()
    user_id = data.get("user_id") or str(uuid.uuid4())
    query = data.get("query")
    lat = data.get("lat")
    lng = data.get("lng")
    timestamp = data.get("timestamp") or time.time()

    # 1. Check if session exists
    session = cache.get_user_session(user_id)

    # 2. Determine whether to reuse snapshot
    snapshot_id = None
    snapshot_data = None
    if session:
        last_snapshot_id = session.get("last_snapshot_id")
        if last_snapshot_id:
            snapshot_data = cache.get_snapshot(last_snapshot_id)
            # You can add bounding box / route segment check here for partial reuse
            snapshot_id = last_snapshot_id

    # 3. If no valid snapshot, fetch fresh data
    if not snapshot_data:
        # For simplicity, assume user wants a fixed destination in this demo
        destination = query  # in real, parse intent with LLM
        route_data = maps_client.get_directions(lat, lng, destination)
        weather_data = weather_client.get_weather(destination)
        snapshot_data = {
            "snapshot_id": str(uuid.uuid4()),
            "origin": {"lat": lat, "lng": lng},
            "destination": destination,
            "routes": route_data,
            "weather": weather_data,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        snapshot_id = snapshot_data["snapshot_id"]
        cache.save_snapshot(snapshot_id, snapshot_data)

    # 4. Update user session
    cache.update_user_session(user_id, {
        "last_snapshot_id": snapshot_id,
        "last_location": {"lat": lat, "lng": lng},
        "last_query": query,
        "timestamp": timestamp
    })

    # 5. Call LLM to generate user-friendly response
    response_text = llm_client.generate_response(query, snapshot_data)

    return JSONResponse({
        "text": response_text,
        "snapshot_id": snapshot_id,
        "user_id": user_id
    })
