import os
import platform
from pathlib import Path


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
    "ordered": {"routeId", "waypoints"},
}

# Valid request types
VALID_REQUEST_TYPES = set(KEYS_PARAMETERS.keys())

# Valid criterion values
VALID_CRITERIA = {"distance", "duration", "ordered"}

# Default criterion
DEFAULT_CRITERION = "distance"

PROJECT_PATH = Path(__file__).parents[2]

# Detecta o sistema operacional
is_windows = platform.system() == "Windows"

# Define o diretório base de cache conforme o sistema echo %PROGRAMDATA%
if is_windows:
    OSMR_PATH_CACHE = Path(os.environ.get("PROGRAMDATA")) / "ANATEL"
else:
    OSMR_PATH_CACHE = Path.home() / ".cache" / "anatel"

OSMR_PATH_CACHE.mkdir(parents=True, exist_ok=True)

# Define os caminhos finais
LOGS_PATH = PROJECT_PATH / "logs"

LOGS_PATH.mkdir(parents=True, exist_ok=True)
