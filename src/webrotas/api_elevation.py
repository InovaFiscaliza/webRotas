import math
import requests

TIMEOUT = 10
BATCH_SIZE = 100  # Maximum points per request
URL = [
    "https://api.open-elevation.com/api/v1/lookup",
    "http://rhfisnspdex02.anatel.gov.br/api/v1/lookup"
]

#-----------------------------------------------------------------------------------#
def controller(origin, waypoints):
    points = [origin] + waypoints

    if not needs_elevation(points):
        return origin, waypoints
    
    # ToDo: evoluir, de forma que sejam pedidos apenas pontos que não possuem elevation

    for url in URL:
        elevations, fetch_status = get_elevation(url, points)
        if fetch_status:
            break

    origin["elevation"] = elevations[0]
    for ii, wp in enumerate(waypoints, start=1):
        wp["elevation"] = elevations[ii]

    return origin, waypoints

#-----------------------------------------------------------------------------------#
def needs_elevation(points):
    for p in points:
        elevation = p.get("elevation")
        if not isinstance(elevation, (int, float)):
            return True
        if isinstance(elevation, float) and math.isnan(elevation):
            return True
        if elevation == -9999:
            return True
    return False

#-----------------------------------------------------------------------------------#
def get_elevation(url, points):
    """Fetch elevation data in batches to avoid API rejection on large requests."""
    if not points:
        return [], True
    
    all_elevations = []
    
    # Process points in batches
    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i:i + BATCH_SIZE]
        batch_elevations, success = _fetch_elevation_batch(url, batch)
        
        if not success:
            return [-9999] * len(points), False
        
        all_elevations.extend(batch_elevations)
    
    return all_elevations, True

#-----------------------------------------------------------------------------------#
def _fetch_elevation_batch(url, points):
    """Fetch elevation for a single batch of points."""
    coord_str  = "|".join(f"{c['lat']},{c['lng']}" for c in points)
    parameters = {"locations": coord_str}

    try:
        response = requests.get(url, params=parameters, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError):
        return [-9999] * len(points), False
    
    results = data.get("results")
    if isinstance(results, list) and len(results) == len(points):
        try:
            return [round(res["elevation"], 1) for res in results], True
        except (KeyError, TypeError):
            return [-9999] * len(points), False
    else:
        return [-9999] * len(points), False
