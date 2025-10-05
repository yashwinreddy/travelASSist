# utils.py
import math
import polyline

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Returns distance in meters between two lat/lng points using Haversine formula.
    """
    R = 6371000  # radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def is_point_in_bounding_box(point_lat, point_lng, bbox):
    """
    bbox = {"min_lat":.., "max_lat":.., "min_lng":.., "max_lng":..}
    """
    return (bbox["min_lat"] <= point_lat <= bbox["max_lat"] and
            bbox["min_lng"] <= point_lng <= bbox["max_lng"])

def decode_polyline(encoded_polyline):
    """
    Decode Google Maps polyline into list of lat/lng tuples.
    """
    return polyline.decode(encoded_polyline)

def is_point_on_route(point_lat, point_lng, route_polyline, tolerance_meters=100):
    """
    Checks if a point is approximately on a polyline route.
    """
    points = decode_polyline(route_polyline)
    for lat, lng in points:
        if haversine_distance(lat, lng, point_lat, point_lng) <= tolerance_meters:
            return True
    return False
