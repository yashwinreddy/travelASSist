# app/cache_manager.py

import time
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# TTLs in seconds
SNAPSHOT_TTL = 1500  # 25 minutes
SESSION_TTL = 1800   # 30 minutes
SEGMENT_TTL = 900    # 15 minutes
WEATHER_TTL = 600    # 10 minutes

if REDIS_AVAILABLE:
    r = redis.Redis(host='localhost', port=6379, db=0)
else:
    r = {}

def _hash_key(key: str):
    """Create a consistent hash for keys."""
    return hashlib.sha256(key.encode()).hexdigest()

# ---------------- Snapshot ----------------
def save_snapshot(snapshot_id: str, snapshot_data: dict):
    key = f"route_snapshot:{_hash_key(snapshot_id)}"
    if REDIS_AVAILABLE:
        r.setex(key, SNAPSHOT_TTL, str(snapshot_data))
    else:
        r[key] = {"data": snapshot_data, "timestamp": time.time()}

def get_snapshot(snapshot_id: str):
    key = f"route_snapshot:{_hash_key(snapshot_id)}"
    if REDIS_AVAILABLE:
        val = r.get(key)
        return eval(val) if val else None
    else:
        entry = r.get(key)
        if entry and time.time() - entry["timestamp"] < SNAPSHOT_TTL:
            return entry["data"]
        return None

# ---------------- User Session ----------------
def save_user_session(user_id: str, session_data: dict):
    key = f"user_session:{_hash_key(user_id)}"
    if REDIS_AVAILABLE:
        r.setex(key, SESSION_TTL, str(session_data))
    else:
        r[key] = {"data": session_data, "timestamp": time.time()}

def get_user_session(user_id: str):
    key = f"user_session:{_hash_key(user_id)}"
    if REDIS_AVAILABLE:
        val = r.get(key)
        return eval(val) if val else None
    else:
        entry = r.get(key)
        if entry and time.time() - entry["timestamp"] < SESSION_TTL:
            return entry["data"]
        return None

# ---------------- Partial Route Segment ----------------
def save_route_segment(route_id: str, segment_index: int, segment_data: dict):
    key = f"route_segment:{_hash_key(route_id)}:{segment_index}"
    if REDIS_AVAILABLE:
        r.setex(key, SEGMENT_TTL, str(segment_data))
    else:
        r[key] = {"data": segment_data, "timestamp": time.time()}

def get_route_segment(route_id: str, segment_index: int):
    key = f"route_segment:{_hash_key(route_id)}:{segment_index}"
    if REDIS_AVAILABLE:
        val = r.get(key)
        return eval(val) if val else None
    else:
        entry = r.get(key)
        if entry and time.time() - entry["timestamp"] < SEGMENT_TTL:
            return entry["data"]
        return None

# ---------------- Weather Point ----------------
def save_weather_point(lat: float, lng: float, weather_data: dict):
    key = f"weather_point:{lat}:{lng}"
    if REDIS_AVAILABLE:
        r.setex(key, WEATHER_TTL, str(weather_data))
    else:
        r[key] = {"data": weather_data, "timestamp": time.time()}

def get_weather_point(lat: float, lng: float):
    key = f"weather_point:{lat}:{lng}"
    if REDIS_AVAILABLE:
        val = r.get(key)
        return eval(val) if val else None
    else:
        entry = r.get(key)
        if entry and time.time() - entry["timestamp"] < WEATHER_TTL:
            return entry["data"]
        return None
