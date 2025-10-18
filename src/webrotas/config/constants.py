"""Request validation constants for webRotas API"""

# Root-level request validation
KEYS_ROOT = {
    "required": {"type", "origin", "parameters"},
    "optional": {"avoidZones", "criterion"},
}

# Parameter validation by request type
KEYS_PARAMETERS = {
    "shortest": {"waypoints"},
    "circle": {"centerPoint", "radius", "totalWaypoints"},
    "grid": {"city", "state", "scope", "pointDistance"},
    "ordered": {"routeId", "cacheId", "boundingBox", "waypoints"},
}

# Valid request types
VALID_REQUEST_TYPES = set(KEYS_PARAMETERS.keys())

# Valid criterion values
VALID_CRITERIA = {"distance", "duration", "ordered"}

# Default criterion
DEFAULT_CRITERION = "distance"
