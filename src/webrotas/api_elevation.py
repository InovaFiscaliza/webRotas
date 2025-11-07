import math
import requests

TIMEOUT = 10
BATCH_SIZE = 100  # Maximum points per request
URL = [
    "https://api.open-elevation.com/api/v1/lookup",
    "http://rhfisnspdex02.anatel.gov.br/api/v1/lookup"
]

#-----------------------------------------------------------------------------------#
def _fetch_elevations_from_endpoints(points):
    """
    Attempt to fetch elevation data from available endpoints.
    
    Tries each endpoint in sequence until one succeeds.
    
    Args:
        points: List of coordinate dicts with 'lat' and 'lng' keys
        
    Returns:
        tuple: (elevations_list, success_bool)
            - elevations_list: List of elevation values or -9999 for failures
            - success_bool: True if elevation fetch succeeded
    """
    # ToDo: evoluir, de forma que sejam pedidos apenas pontos que não possuem elevation
    for url in URL:
        elevations, fetch_status = get_elevation(url, points)
        if fetch_status:
            return elevations, True
    
    return [-9999] * len(points), False


def _assign_elevations_to_waypoints(origin, waypoints, elevations):
    """
    Assign elevation values to origin and waypoint coordinates.
    
    Updates the 'elevation' field for each point in place.
    
    Args:
        origin: Origin coordinate dict
        waypoints: List of waypoint coordinate dicts
        elevations: List of elevation values matching [origin, ...waypoints]
        
    Returns:
        tuple: (origin, waypoints) with elevation fields populated
    """
    origin["elevation"] = elevations[0]
    for ii, wp in enumerate(waypoints, start=1):
        wp["elevation"] = elevations[ii]
    
    return origin, waypoints


def enrich_waypoints_with_elevation(origin, waypoints):
    """
    Enrich waypoint coordinates with elevation data.
    
    This is the main entry point for elevation retrieval. It orchestrates:
    1. Checking if elevation data is needed
    2. Fetching from available endpoints
    3. Assigning elevation values to waypoints
    
    Args:
        origin: Starting coordinate dict with 'lat' and 'lng' keys
        waypoints: List of waypoint coordinate dicts
        
    Returns:
        tuple: (origin, waypoints) with 'elevation' field populated for each point
                Returns -9999 for elevation if fetch fails or endpoint unavailable
    """
    points = [origin] + waypoints
    
    # Skip fetch if all points already have valid elevation data
    if not needs_elevation(points):
        return origin, waypoints
    
    # Fetch elevation from available endpoints
    elevations, _ = _fetch_elevations_from_endpoints(points)
    
    # Assign elevations to waypoints
    return _assign_elevations_to_waypoints(origin, waypoints, elevations)


def controller(origin, waypoints):
    """
    Legacy wrapper for enrich_waypoints_with_elevation.
    
    Maintained for backward compatibility. Use enrich_waypoints_with_elevation() for new code.
    
    Args:
        origin: Starting coordinate dict with 'lat' and 'lng' keys
        waypoints: List of waypoint coordinate dicts
        
    Returns:
        tuple: (origin, waypoints) with 'elevation' field populated
    """
    return enrich_waypoints_with_elevation(origin, waypoints)

#-----------------------------------------------------------------------------------#
def needs_elevation(points):
    """
    Check if any point lacks valid elevation data.
    
    A point is considered to need elevation if:
    - 'elevation' field is missing or not a number
    - 'elevation' is NaN (floating point)
    - 'elevation' is -9999 (error sentinel value)
    
    Args:
        points: List of coordinate dicts with optional 'elevation' field
        
    Returns:
        bool: True if any point needs elevation data, False if all have valid data
    """
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
    """
    Fetch elevation data for points from a specific endpoint.
    
    Processes points in batches to avoid API rejection on large requests.
    Uses BATCH_SIZE constant to chunk requests appropriately.
    
    Args:
        url: Elevation API endpoint URL
        points: List of coordinate dicts with 'lat' and 'lng' keys
        
    Returns:
        tuple: (elevations_list, success_bool)
            - elevations_list: List of elevation values or [-9999] * len(points) on failure
            - success_bool: True if all batches succeeded, False if any batch failed
    """
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
    """
    Fetch elevation data for a single batch of points from API.
    
    Makes a single HTTP request to the elevation endpoint and parses the response.
    Returns -9999 sentinel value for any points if the request fails or response is invalid.
    
    Args:
        url: Elevation API endpoint URL
        points: List of coordinate dicts with 'lat' and 'lng' keys
        
    Returns:
        tuple: (elevations_list, success_bool)
            - elevations_list: List of elevation values rounded to 1 decimal or [-9999] * len(points) on failure
            - success_bool: True if fetch and parsing succeeded, False otherwise
    """
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
