# routes.py
from fastapi import APIRouter, Query
import requests
import time

router = APIRouter()


CACHE = {}
CACHE_TTL = 1800  # 30 mins

GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

def is_cache_valid(entry):
    return time.time() - entry["timestamp"] < CACHE_TTL

@router.get("/route-info")
def get_route_info(
    origin_lat: float = Query(...),
    origin_lng: float = Query(...),
    destination: str = Query(...)
):
    """
    Fetch route info (driving/walking/cycling), traffic, alternates, weather.
    """

    cache_key = f"{origin_lat},{origin_lng}->{destination.lower()}"
    if cache_key in CACHE and is_cache_valid(CACHE[cache_key]):
        return {"source": "cache", **CACHE[cache_key]["data"]}


    base_url = "https://maps.googleapis.com/maps/api/directions/json"

    modes = ["driving", "walking", "bicycling"]
    routes_data = {}

    for mode in modes:
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": destination,
            "mode": mode,
            "alternatives": "true",
            "departure_time": "now",  # enables traffic info
            "key": GOOGLE_MAPS_API_KEY
        }
        res = requests.get(base_url, params=params).json()

        if res["status"] != "OK":
            routes_data[mode] = {"error": res.get("status")}
            continue

        main_route = res["routes"][0]
        distance = main_route["legs"][0]["distance"]["text"]
        duration = main_route["legs"][0]["duration"]["text"]

        # Traffic-aware duration (only for driving)
        traffic = None
        if mode == "driving" and "duration_in_traffic" in main_route["legs"][0]:
            duration = main_route["legs"][0]["duration_in_traffic"]["text"]
            traffic = "Traffic considered"

        # Alternate routes (only for driving)
        alternates = []
        if mode == "driving" and len(res["routes"]) > 1:
            for alt in res["routes"][1:]:
                alt_distance = alt["legs"][0]["distance"]["text"]
                alt_duration = alt["legs"][0]["duration"]["text"]
                alt_via = alt["summary"]
                alternates.append(f"{alt_via}: {alt_distance}, {alt_duration}")

        routes_data[mode] = {
            "distance": distance,
            "duration": duration,
            "traffic": traffic,
            "alternates": alternates
        }

    # Weather (OpenWeather API) at destination
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geo_res = requests.get(geocode_url, params={"address": destination, "key": GOOGLE_MAPS_API_KEY}).json()
    if geo_res["status"] == "OK":
        dest_loc = geo_res["results"][0]["geometry"]["location"]
        dest_lat, dest_lng = dest_loc["lat"], dest_loc["lng"]

        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "lat": dest_lat,
            "lon": dest_lng,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        weather_res = requests.get(weather_url, params=weather_params).json()

        weather_info = {
            "status": weather_res["weather"][0]["description"],
            "temperature": f"{weather_res['main']['temp']}°C"
        }
    else:
        weather_info = {"error": "Could not fetch weather"}

    response = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": destination,
        "routes": routes_data,
        "weather": weather_info,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

    # Save to cache
    CACHE[cache_key] = {"data": response, "timestamp": time.time()}

    return {"source": "api", **response}
