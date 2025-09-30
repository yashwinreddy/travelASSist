# app/routes.py
from fastapi import APIRouter, Query, HTTPException
import requests
import time

router = APIRouter()

# Simple in-memory cache
CACHE = {}
CACHE_TTL = 1800  # 30 mins

# API Keys (replace with env vars in prod)
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"


def is_cache_valid(entry: dict) -> bool:
    """Check if cache entry is still valid."""
    return time.time() - entry["timestamp"] < CACHE_TTL


def fetch_weather(destination: str) -> dict:
    """Fetch weather info for a destination using Google Geocode + OpenWeather."""
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geo_res = requests.get(
        geocode_url, params={"address": destination, "key": GOOGLE_MAPS_API_KEY}
    ).json()

    if geo_res.get("status") != "OK":
        return {"error": "Could not fetch coordinates for weather"}

    dest_loc = geo_res["results"][0]["geometry"]["location"]
    dest_lat, dest_lng = dest_loc["lat"], dest_loc["lng"]

    weather_url = "http://api.openweathermap.org/data/2.5/weather"
    weather_params = {
        "lat": dest_lat,
        "lon": dest_lng,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    weather_res = requests.get(weather_url, params=weather_params).json()

    if "weather" not in weather_res or "main" not in weather_res:
        return {"error": "Weather API failed"}

    return {
        "status": weather_res["weather"][0]["description"],
        "temperature": f"{weather_res['main']['temp']}°C",
    }


def fetch_routes(origin: str, destination: str) -> dict:
    """Fetch routes for driving, walking, cycling."""
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    modes = ["driving", "walking", "bicycling"]
    routes_data = {}

    for mode in modes:
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "alternatives": "true",
            "departure_time": "now",  # enables traffic info
            "key": GOOGLE_MAPS_API_KEY,
        }
        res = requests.get(base_url, params=params).json()

        if res.get("status") != "OK":
            routes_data[mode] = {"error": res.get("status", "Unknown error")}
            continue

        # Always take first route as main
        leg = res["routes"][0]["legs"][0]
        distance = leg["distance"]["text"]
        duration = leg["duration"]["text"]

        # Traffic-aware duration (driving only)
        traffic = None
        if mode == "driving" and "duration_in_traffic" in leg:
            duration = leg["duration_in_traffic"]["text"]
            traffic = "Traffic considered"

        # Collect alternates (driving only)
        alternates = []
        if mode == "driving" and len(res["routes"]) > 1:
            for alt in res["routes"][1:]:
                alt_leg = alt["legs"][0]
                alternates.append({
                    "via": alt.get("summary", "Unnamed Road"),
                    "distance": alt_leg["distance"]["text"],
                    "duration": alt_leg["duration"]["text"],
                })

        routes_data[mode] = {
            "distance": distance,
            "duration": duration,
            "traffic": traffic,
            "alternates": alternates,
        }

    return routes_data


@router.get("/route-info")
def get_route_info(
    origin_lat: float = Query(..., description="Origin latitude"),
    origin_lng: float = Query(..., description="Origin longitude"),
    destination: str = Query(..., description="Destination address or place"),
):
    """
    Get route information for driving, walking, cycling
    + traffic + alternate routes + destination weather.
    Cached for 30 minutes to reduce API calls.
    """

    origin = f"{origin_lat},{origin_lng}"
    cache_key = f"{origin}->{destination.lower()}"

    # Serve from cache if available
    if cache_key in CACHE and is_cache_valid(CACHE[cache_key]):
        return {"source": "cache", **CACHE[cache_key]["data"]}

    try:
        routes_data = fetch_routes(origin, destination)
        weather_info = fetch_weather(destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upstream API error: {str(e)}")

    response = {
        "origin": origin,
        "destination": destination,
        "routes": routes_data,
        "weather": weather_info,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    }

    # Save to cache
    CACHE[cache_key] = {"data": response, "timestamp": time.time()}

    return {"source": "api", **response}
