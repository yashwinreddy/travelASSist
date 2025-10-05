# app/api_client.py

import requests
from typing import Dict, List
from app.cache_manager import save_snapshot, save_weather_point
import time
import polyline  # to handle route polylines

GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

def fetch_directions(origin_lat: float, origin_lng: float, destination: str, modes: List[str] = ["driving","walking","bicycling"]) -> Dict:
    """Fetch routes for all requested modes and return compact snapshot."""
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    routes_data = {}

    for mode in modes:
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": destination,
            "mode": mode,
            "alternatives": "true",
            "departure_time": "now",
            "key": GOOGLE_MAPS_API_KEY
        }
        res = requests.get(base_url, params=params).json()

        if res["status"] != "OK":
            routes_data[mode] = {"error": res.get("status")}
            continue

        main_route = res["routes"][0]
        leg = main_route["legs"][0]

        distance_km = leg["distance"]["value"] / 1000
        duration_min = leg["duration"]["value"] // 60

        # Traffic-aware duration for driving
        if mode == "driving" and "duration_in_traffic" in leg:
            duration_min = leg["duration_in_traffic"]["value"] // 60

        # Store route summary
        summary = main_route.get("summary", "")
        polyline_points = main_route.get("overview_polyline", {}).get("points", "")

        # Alternate routes (for driving)
        alternates = []
        if mode == "driving" and len(res["routes"]) > 1:
            for alt in res["routes"][1:]:
                alt_leg = alt["legs"][0]
                alt_distance = alt_leg["distance"]["value"] / 1000
                alt_duration = alt_leg["duration"]["value"] // 60
                alt_summary = alt.get("summary", "")
                alternates.append({
                    "summary": alt_summary,
                    "distance_km": alt_distance,
                    "eta_min": alt_duration
                })

        routes_data[mode] = {
            "distance_km": distance_km,
            "eta_min": duration_min,
            "route_summary": summary,
            "polyline": polyline_points,
            "alternates": alternates
        }

    return routes_data

def fetch_weather(lat: float, lng: float) -> Dict:
    """Fetch weather at a specific point."""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    res = requests.get(url, params=params).json()
    weather_info = {
        "status": res["weather"][0]["description"],
        "temperature": f"{res['main']['temp']}°C"
    }
    # Save weather point in cache
    save_weather_point(lat, lng, weather_info)
    return weather_info

def build_snapshot(origin_lat: float, origin_lng: float, destination_name: str, destination_lat: float, destination_lng: float) -> Dict:
    """Combine directions and weather into a compact snapshot for LLM."""
    snapshot_id = f"{origin_lat},{origin_lng}->{destination_name.lower()}:{int(time.time())}"
    routes = fetch_directions(origin_lat, origin_lng, destination_name)
    weather_dest = fetch_weather(destination_lat, destination_lng)

    snapshot = {
        "snapshot_id": snapshot_id,
        "origin": {"lat": origin_lat, "lng": origin_lng},
        "destination": {"name": destination_name, "lat": destination_lat, "lng": destination_lng},
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "routes": routes,
        "weather": weather_dest
    }

    # Save snapshot to cache
    save_snapshot(snapshot_id, snapshot)
    return snapshot
