import json
import os
from dataclasses import dataclass
import math
from pathlib import Path
from typing import List, Tuple, Iterable, Dict, Any, Optional
from fastapi import HTTPException

# Client-side zone processing imports
import httpx
from shapely.geometry import LineString, shape
from shapely.strtree import STRtree

from geopy.distance import geodesic
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from webrotas.config.logging_config import get_logger
from webrotas.iterative_matrix_builder import IterativeMatrixBuilder
from webrotas.config.server_hosts import get_osrm_url
from webrotas.geojson_converter import avoid_zones_to_geojson
from webrotas.segment_alternatives import get_alternatives_for_multipoint_route
from webrotas.zone_aware_routing import find_route_around_zones

from .lua_converter import write_lua_zones_file
from .version_manager import save_version


# Initialize logging at module level
logger = get_logger(__name__)


TIMEOUT = 10
URL = {
    "table": lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}

TEST_ROUTE = "/route/v1/driving/-43.105772903105354,-22.90510838815471;-43.089637952126694,-22.917360518277434?overview=full&geometries=polyline&steps=true"
ALTERNATIVES = 3

# ============================================================================
# Configuration
# ============================================================================

OSRM_PROFILE = os.getenv("OSRM_PROFILE", "/profiles/car_avoid.lua")
PBF_NAME = os.getenv("PBF_NAME", "region.osm.pbf")
OSRM_BASE = os.getenv("OSRM_BASE", "region")
AVOIDZONES_TOKEN = os.getenv("AVOIDZONES_TOKEN", "default-token")
OSRM_DATA_DIR = Path(os.getenv("OSRM_DATA", "/data"))
OSM_PBF_URL = os.getenv("OSM_PBF_URL", "")

# OSRM server URL for routing requests
OSRM_URL = os.getenv("OSRM_URL", "http://localhost:5000")

# Docker resource limits for OSRM preprocessing
DOCKER_MEMORY_LIMIT = os.getenv("DOCKER_MEMORY_LIMIT", "16g")
DOCKER_CPUS_LIMIT = float(os.getenv("DOCKER_CPUS_LIMIT", "4.0"))

# History and state directories
HISTORY_DIR = OSRM_DATA_DIR / "avoidzones_history"
LATEST_POLYGONS = OSRM_DATA_DIR / "latest_avoidzones.geojson"
LUA_ZONES_FILE = OSRM_DATA_DIR / "profiles" / "avoid_zones_data.lua"

HISTORY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class UserData:
    OSMRport: int = 5000
    ssid: str | None = None


# ============================================================================
# Client-Side Zone Processing Helpers
# ============================================================================


def process_avoidzones(geojson: dict) -> None:
    """
    Process avoid zones:
    1. Save the geojson to history (with deduplication)
    2. Convert polygons to Lua format
    3. Start PBF reprocessing in background thread (non-blocking)

    Returns the version identifier (e.g., "v5") of the configuration,
    which may be an existing duplicate or a newly created version.
    PBF reprocessing happens in the background for new versions.
    """
    # Validate GeoJSON
    if geojson.get("type") != "FeatureCollection":
        raise ValueError("Expected FeatureCollection")

    # Save to history with deduplication
    version_filename, is_new_version = save_version(
        geojson, HISTORY_DIR, check_duplicates=True
    )
    logger.info(f"Saved avoidzones version: {version_filename} (new={is_new_version})")

    # Save as latest
    LATEST_POLYGONS.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    logger.info(f"Saved as latest polygons: {LATEST_POLYGONS}")

    # Convert to Lua format
    try:
        logger.info("Converting polygons to Lua format...")
        if write_lua_zones_file(LATEST_POLYGONS, LUA_ZONES_FILE):
            logger.info(f"Lua zones file written to {LUA_ZONES_FILE}")
        else:
            logger.warning("Failed to write Lua zones file, continuing anyway")
    except Exception as e:
        logger.error(f"Failed to convert polygons to Lua: {e}")
        logger.warning("Continuing despite Lua conversion error")


def load_spatial_index(geojson: Dict[str, Any]) -> tuple[List, Optional[STRtree]]:
    """
    Build spatial index from GeoJSON for fast polygon queries.

    Args:
        geojson: GeoJSON FeatureCollection or Feature

    Returns:
        Tuple of (list of shapely polygons, STRtree spatial index)
        Returns ([], None) if no valid polygons found
    """
    try:
        features = (
            geojson.get("features", [])
            if geojson.get("type") == "FeatureCollection"
            else [geojson]
        )

        polys = []
        for feature in features:
            geom = feature.get("geometry")
            if geom and geom.get("type") in ("Polygon", "MultiPolygon"):
                try:
                    poly = shape(geom)
                    if poly.is_valid:
                        polys.append(poly)
                except Exception as e:
                    logger.warning(f"Could not convert geometry to polygon: {e}")
                    continue

        if not polys:
            logger.info("No valid polygons found in GeoJSON")
            return [], None

        tree = STRtree(polys)
        return polys, tree
    except Exception as e:
        logger.error(f"Error building spatial index: {e}")
        return [], None


def check_route_intersections(
    coords: List[List[float]], polygons: List, tree: Optional[STRtree]
) -> Dict[str, Any]:
    """
    Calculate route-polygon intersections for a given route and set of avoid zone polygons.

    Args:
        coords: List of [longitude, latitude] coordinates forming the route
        polygons: List of shapely polygon objects representing avoid zones
        tree: STRtree spatial index of polygons (or None if no polygons)

    Returns:
        Dictionary with intersection statistics:
        - intersection_count: Number of polygons route intersects
        - total_length_km: Total length of route within avoid zones
        - penalty_ratio: Fraction of route within zones (0.0-1.0)
        - route_length_km: Total route length in kilometers
    """
    if not polygons or tree is None:
        return {
            "intersection_count": 0,
            "total_length_km": 0.0,
            "penalty_ratio": 0.0,
            "route_length_km": 0.0,
        }

    try:
        route_line = LineString(coords)
        intersection_count = 0
        total_intersection_length = 0

        # Query spatial index for candidate polygons
        candidate_indices = tree.query(route_line)

        for idx in candidate_indices:
            polygon = polygons[idx]
            if route_line.intersects(polygon):
                intersection_count += 1
                intersection = route_line.intersection(polygon)
                # Handle both Point and LineString/MultiLineString intersections
                if hasattr(intersection, "length"):
                    total_intersection_length += intersection.length

        total_route_length = route_line.length
        penalty_ratio = (
            total_intersection_length / total_route_length
            if total_route_length > 0
            else 0.0
        )

        # Convert to km for readability
        total_intersection_km = total_intersection_length / 1000
        route_length_km = total_route_length / 1000

        return {
            "intersection_count": intersection_count,
            "total_length_km": round(total_intersection_km, 3),
            "penalty_ratio": min(penalty_ratio, 1.0),  # Cap at 100%
            "route_length_km": round(route_length_km, 3),
        }
    except Exception as e:
        logger.error(f"Error calculating route intersections: {e}")
        return {
            "intersection_count": 0,
            "total_length_km": 0.0,
            "penalty_ratio": 0.0,
            "route_length_km": 0.0,
        }


async def route_with_zones(
    coordinates: str,
    geojson: Dict[str, Any],
    avoid_mode: str = "penalize",
    alternatives: int = ALTERNATIVES,
) -> Dict[str, Any]:
    """
    Route with client-side avoid zones filtering.

    Request route from OSRM, then filter/penalize based on avoid zones.

    Args:
        coordinates: OSRM format "lng1,lat1;lng2,lat2"
        geojson: GeoJSON object representing avoid zones
        avoid_mode: "filter" (exclude routes in zones) or "penalize" (return all routes with scores)
        alternatives: Number of alternative routes (1-3)

    Returns:
        OSRM response with added penalties and zones metadata
    """
    try:
        # Validate avoid_mode
        if avoid_mode not in ("filter", "penalize"):
            raise HTTPException(
                status_code=400,
                detail="avoid_mode must be 'filter' or 'penalize'",
            )

        # Load zones configuration
        polys, tree = load_spatial_index(geojson)

        polygon_count = len(polys)
        logger.info(f"Loaded {polygon_count} avoid zone polygons")

        # Request route from OSRM
        logger.info(f"Requesting {alternatives} alternative route(s) from OSRM")
        params = {
            "alternatives": alternatives,
            "overview": "full",
            "geometries": "geojson",
        }
        osrm_response = await request_osrm(
            request_type="route",
            coordinates=coordinates,
            params=params,
        )

        if not osrm_response.get("routes"):
            logger.warning("No routes found from OSRM")
            return osrm_response

        # Process routes through zones
        processed_routes = []
        intersection_info = {}

        for idx, route in enumerate(osrm_response["routes"]):
            coords = route["geometry"]["coordinates"]
            intersection_data = check_route_intersections(coords, polys, tree)

            # Apply avoid mode logic
            if avoid_mode == "filter" and intersection_data["intersection_count"] > 0:
                logger.info(
                    f"Route {idx} filtered (crosses {intersection_data['intersection_count']} zones)"
                )
                continue  # Skip routes with intersections
            elif avoid_mode == "penalize":
                # Add penalty information to route
                if "penalties" not in route:
                    route["penalties"] = {}
                route["penalties"] = {
                    "zone_intersections": intersection_data["intersection_count"],
                    "intersection_length_km": intersection_data["total_length_km"],
                    "penalty_score": intersection_data["penalty_ratio"],
                }

            processed_routes.append(route)
            intersection_info[f"route_{len(processed_routes) - 1}"] = intersection_data

        # Sort routes by penalty score (best first)
        if avoid_mode == "penalize":
            processed_routes.sort(
                key=lambda r: r.get("penalties", {}).get("penalty_score", 0)
            )

        # Return processed response
        osrm_response["routes"] = processed_routes
        osrm_response["zones_applied"] = {
            "version": "latest",
            "polygon_count": polygon_count,
        }
        osrm_response["intersection_info"] = intersection_info

        logger.info(
            f"Returning {len(processed_routes)} route(s) with {polygon_count} zones applied"
        )
        return osrm_response

    except FileNotFoundError as e:
        logger.error(f"Zones file not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid version format: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in route_with_zones: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")


async def make_request(url, params=None):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def request_osrm(
    request_type: str,
    coordinates: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Request route from OSRM with specified parameters.

    Args:
        coordinates: OSRM format coordinates "lng1,lat1;lng2,lat2"
        alternatives: Number of alternative routes (1-3)
        overview: Detail level ("simplified", "full", "false")
        geometries: Geometry format ("geojson", "polyline", "polyline6")

    Returns:
        OSRM response as dictionary

    Raises:
        HTTPException: On connection or OSRM errors
    """
    try:
        assert request_type in {"route", "table"}, "Invalid request type"
        url = f"{get_osrm_url()}/{request_type}/v1/driving/{coordinates}"
        data = await make_request(url, params=params)
        return data

    except httpx.HTTPError as e:
        logger.error(f"OSRM HTTP error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"OSRM routing request failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error requesting OSRM: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error requesting OSRM: {str(e)}",
        )


# -----------------------------------------------------------------------------------#
async def compute_distance_and_duration_matrices(
    coords, avoid_zones: Iterable | None = None
):
    """
    Retrieve distance and duration matrices using fallback strategy.

    Attempts to fetch routing matrices in this order:
    1. Local container (if many points or avoidance zones present)
    2. Public OSRM API
    3. Iterative matrix builder (for large datasets)
    4. Geodesic fallback (as last resort)

    Args:
        coords: List of coordinate dicts with 'lat' and 'lng' keys
        avoid_zones: Optional iterable of avoidance zones

    Returns:
        tuple: (distances, durations) matrices
    """
    use_container = _should_use_local_container(coords, avoid_zones)

    if use_container:
        return await _get_matrix_with_local_container_priority(coords, avoid_zones)
    return await _get_matrix_with_public_api_priority(coords)


def _should_use_local_container(coords, avoid_zones: Iterable | None = None) -> bool:
    """
    Determine if local container should be used for routing.

    Local container is preferred when:
    - More than 100 points (exceeds public API limits)
    - Avoidance zones are present (require local processing)

    Args:
        coords: List of coordinates
        avoid_zones: Optional iterable of avoidance zones

    Returns:
        bool: True if local container should be used
    """
    if len(coords) > 100:
        logger.info(
            f"Too many points ({len(coords)}), using local container or iterative matrix"
        )
        return True

    if avoid_zones is not None and len(avoid_zones) > 0:
        logger.info(
            f"Exclusion zones present ({len(avoid_zones)}), using local container"
        )
        return True

    return False


async def _get_matrix_with_local_container_priority(coords, avoid_zones):
    """
    Attempt to retrieve matrix starting with local container.

    Fallback chain:
    1. Local OSRM container
    2. Iterative matrix builder (if no avoidance zones)
    3. Geodesic calculation

    Args:
        coords: List of coordinates
        avoid_zones: Optional iterable of avoidance zones

    Returns:
        tuple: (distances, durations) matrices
    """
    try:
        return await get_osrm_matrix_from_local_container(coords)
    except Exception as e:
        if avoid_zones is None:
            logger.error(
                f"Local container failed: {e}. 🟢 NO Avoidance Zones Present. Trying iterative matrix builder",
                exc_info=True,
            )
            try:
                return get_osrm_matrix_iterative(coords)
            except Exception as iterative_e:
                logger.warning(
                    f"Iterative matrix builder also failed: {iterative_e}. Using geodesic calculation"
                )
                return get_geodesic_matrix(coords, speed_kmh=40)
        else:
            logger.error(
                f"Local container failed: {e}. 🚫 Avoidance Zones present. Using geodesic calculation",
                exc_info=True,
            )
            return get_geodesic_matrix(coords, speed_kmh=40)


async def _get_matrix_with_public_api_priority(coords):
    """
    Attempt to retrieve matrix starting with public OSRM API.

    Fallback chain:
    1. Public OSRM API
    2. Local OSRM container
    3. Iterative matrix builder
    4. Geodesic calculation

    Args:
        coords: List of coordinates

    Returns:
        tuple: (distances, durations) matrices
    """
    try:
        return await get_osrm_matrix(coords)
    except (httpx.HTTPError, ValueError, KeyError) as e:
        logger.error(f"Public API failed: {e}. Trying local container", exc_info=True)
        try:
            return await get_osrm_matrix_from_local_container(coords)
        except Exception as container_e:
            logger.warning(
                f"Local container also failed: {container_e}. Trying iterative matrix builder"
            )
            try:
                return get_osrm_matrix_iterative(coords)
            except Exception as iterative_e:
                logger.warning(
                    f"Iterative matrix builder also failed: {iterative_e}. Using geodesic calculation"
                )
                return get_geodesic_matrix(coords, speed_kmh=40)


def _ensure_valid_matrices(coords, distances, durations):
    """
    Validate and repair distance/duration matrices.

    Performs validation checks and attempts to fix invalid pairs using geodesic calculation.
    If validation fails completely, falls back to full geodesic calculation.

    Args:
        coords: List of coordinates
        distances: Distance matrix
        durations: Duration matrix

    Returns:
        tuple: (distances, durations) valid matrices
    """
    mat = validate_matrix(coords, distances, durations)

    if mat is None:
        logger.error("Matrix validation failed, falling back to geodesic calculation")
        return get_geodesic_matrix(coords, speed_kmh=40)

    distances, durations, invalid_pairs = mat
    if invalid_pairs:
        # Only calculate geodesic for invalid pairs
        logger.warning(
            f"Found {len(invalid_pairs)} invalid pairs, calculating geodesic only for those"
        )
        geodesic_distances, geodesic_durations = get_geodesic_matrix(
            coords, speed_kmh=40, invalid_pairs=invalid_pairs
        )
        # Merge geodesic values into existing matrices
        for i, j in invalid_pairs:
            distances[i][j] = geodesic_distances[i][j]
            durations[i][j] = geodesic_durations[i][j]

    return distances, durations


def _calculate_route_order(coords, distances, durations, criterion: str = "distance"):
    """
    Calculate optimal waypoint visitation order using TSP.

    Solves the open Traveling Salesman Problem based on the specified criterion.
    If criterion is invalid, returns natural order (no optimization).

    Args:
        coords: List of coordinates (unused but kept for consistency)
        distances: Distance matrix
        durations: Duration matrix
        criterion: Optimization criterion ('distance' or 'duration')

    Returns:
        list: Indices representing optimal visitation order
    """
    if criterion in ["distance", "duration"]:
        matrix = distances if criterion == "distance" else durations
        return solve_open_tsp_from_matrix(matrix)
    else:
        logger.warning(f"Unknown criterion '{criterion}', using natural order")
        return list(range(len(coords)))


def _format_route_output(route_json, ordered_coords):
    """
    Extract and format route output from OSRM response.

    Reverses path coordinates and formats duration and distance for display.

    Args:
        route_json: OSRM route response
        ordered_coords: Ordered list of coordinates

    Returns:
        tuple: (origin, waypoints, paths, duration_str, distance_str)
    """
    paths = [
        list(reversed(path))
        for path in route_json["routes"][0]["geometry"]["coordinates"]
    ]
    estimated_sec = route_json["routes"][0]["duration"]
    estimated_m = route_json["routes"][0]["distance"]

    return (
        ordered_coords[0],
        ordered_coords[1:],
        paths,
        seconds_to_hms(estimated_sec),
        f"{round(estimated_m / 1000, 1)} km",
    )


async def calculate_optimal_route(
    origin, waypoints, criterion: str = "distance", avoid_zones: Iterable | None = None
):
    """
    Calculate optimal route visiting origin and waypoints.

    This is the main entry point for route optimization. It orchestrates:
    1. Matrix retrieval with intelligent fallback strategy
    2. Matrix validation and repair
    3. TSP solving for waypoint order optimization
    4. OSRM route calculation
    5. Output formatting

    Args:
        origin: Starting coordinate dict with 'lat' and 'lng' keys
        waypoints: List of waypoint coordinate dicts
        criterion: Optimization criterion ('distance' or 'duration', default: 'distance')
        avoid_zones: Optional iterable of avoidance zones

    Returns:
        tuple: (origin, waypoints, paths, duration_hms, distance_km)
            - origin: First waypoint coordinate
            - waypoints: Remaining optimized waypoint coordinates
            - paths: Route geometry paths
            - duration_hms: Formatted duration (HH:MM:SS)
            - distance_km: Formatted distance (km)
    """
    coords = [origin] + waypoints

    # Retrieve distance/duration matrices with fallback strategy
    distances, durations = await compute_distance_and_duration_matrices(
        coords, avoid_zones
    )

    # Validate and repair matrices
    distances, durations = _ensure_valid_matrices(coords, distances, durations)

    # Calculate optimal waypoint order
    order = _calculate_route_order(coords, distances, durations, criterion)

    # Get route geometry from OSRM
    route_json, ordered_coords = await get_osrm_route(
        coords, order, avoid_zones=avoid_zones
    )

    # Format and return output
    return _format_route_output(route_json, ordered_coords)


async def get_osrm_matrix(coords):
    try:
        coord_str = ";".join(f"{c['lng']},{c['lat']}" for c in coords)
        params = {
            "annotations": "distance,duration",
        }
        data = await request_osrm(
            request_type="table",
            coordinates=coord_str,
            params=params,
        )
        return data["distances"], data["durations"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_osrm_matrix: {e}")
        raise


# -----------------------------------------------------------------------------------#
def get_osrm_matrix_iterative(coords):
    """
    Get distance and duration matrix using iterative batching for large coordinate sets.

    This function uses the IterativeMatrixBuilder to split coordinates into batches
    respecting the public API's 100-waypoint limit, making multiple requests with
    rate limiting and automatic fallback to geodesic calculation for failed pairs.

    Args:
        coords: List of coordinates [{"lat": float, "lng": float}, ...]

    Returns:
        tuple: (distances, durations) matrices

    Raises:
        Exception: If the iterative matrix build fails completely
    """
    logger.info(f"Using iterative matrix builder for {len(coords)} coordinates")
    builder = IterativeMatrixBuilder(coords)
    return builder.build()


def compute_bounding_box(coords):
    """Calculate bounding box with padding for routing"""
    lats = [c["lat"] for c in coords]
    lngs = [c["lng"] for c in coords]

    lat_min, lat_max = min(lats), max(lats)
    lng_min, lng_max = min(lngs), max(lngs)

    # Add padding for routing (50km as in web_rotas.py)
    padding_km = 50
    lat_diff = padding_km / 111.0  # Approximately 1 degree = 111 km
    lng_diff = padding_km / (111.0 * math.cos(math.radians((lat_min + lat_max) / 2)))

    lat_min = round(lat_min - lat_diff, 6)
    lat_max = round(lat_max + lat_diff, 6)
    lng_min = round(lng_min - lng_diff, 6)
    lng_max = round(lng_max + lng_diff, 6)

    return [
        [lat_max, lng_min],
        [lat_max, lng_max],
        [lat_min, lng_max],
        [lat_min, lng_min],
    ]


# -----------------------------------------------------------------------------------#
async def get_osrm_matrix_from_local_container(coords):
    """
    Get distance and duration matrix from local OSRM container.

    This function:
    3. Estimates bounding box for the route
    4. Checks if there's an active container for this area
    5. If not, starts a new container
    6. Makes the request to the local container

    Args:
        coords: List of coordinates [{"lat": float, "lng": float}, ...]

    Returns:
        tuple: (distances, durations) matrices

    Raises:
        Exception: If container setup or request fails, or if port 5000 is not available
    """

    try:
        # Extract bounding box from coordinates
        if not coords or len(coords) < 2:
            raise ValueError("Need at least 2 coordinates for routing")

        # Set up user data for container interface
        if not hasattr(UserData, "ssid") or UserData.ssid is None:
            import uuid

            UserData.ssid = str(uuid.uuid4())[:8]

        # Make request to local container
        coord_str = ";".join(f"{c['lng']},{c['lat']}" for c in coords)

        logger.info(f"Making request to OSRM at: {get_osrm_url()}")

        params = {
            "annotations": "distance,duration",
        }
        data = await request_osrm(
            request_type="table",
            coordinates=coord_str,
            params=params,
        )

        if "distances" not in data or "durations" not in data:
            raise ValueError("Invalid response from local OSRM container")

        logger.info(
            f"Successfully got matrix from local container: {len(data['distances'])}x{len(data['distances'][0])} points"
        )

        return data["distances"], data["durations"]

    except Exception as e:
        logger.error(f"Error in get_osrm_matrix_from_local_container: {e}")
        raise


# -----------------------------------------------------------------------------------#
def get_geodesic_matrix(coords, speed_kmh=40, invalid_pairs=None):
    """
    Calculate geodesic distances between coordinates.

    Args:
        coords: List of coordinate dicts with 'lat' and 'lng' keys
        speed_kmh: Speed in km/h for duration calculation (default: 40)
        invalid_pairs: Optional list of (i, j) tuples for pairs that need geodesic calculation.
                       If None, calculates for all pairs.

    Returns:
        tuple: (distances, durations) matrices
    """
    num_points = len(coords)
    distances = [[0.0] * num_points for _ in range(num_points)]

    # If invalid_pairs provided, only calculate geodesic for those pairs
    if invalid_pairs:
        for ii, jj in invalid_pairs:
            if ii != jj:
                p1 = (coords[ii]["lat"], coords[ii]["lng"])
                p2 = (coords[jj]["lat"], coords[jj]["lng"])
                distances[ii][jj] = geodesic(p1, p2).meters
    else:
        # Calculate for all pairs (fallback for full matrix)
        for ii in range(num_points):
            for jj in range(num_points):
                if ii != jj:
                    p1 = (coords[ii]["lat"], coords[ii]["lng"])
                    p2 = (coords[jj]["lat"], coords[jj]["lng"])
                    distances[ii][jj] = geodesic(p1, p2).meters

    durations = [[(dist / speed_kmh) * 3600 for dist in row] for row in distances]

    return distances, durations


# -----------------------------------------------------------------------------------#
def validate_matrix(
    coords, distances, durations
) -> Tuple[List[float], List[float], List[Tuple[int, int]]] | None:
    num_points = len(coords)
    if distances is None or durations is None:
        return None

    # quick shape checks
    if not (len(distances) == len(durations) == num_points):
        return None
    if any(len(row) != num_points for row in distances) or any(
        len(row) != num_points for row in durations
    ):
        return None

    # Track invalid pairs for potential geodesic calculation
    invalid_pairs = []

    # validate diagonal zeros and positive off-diagonals for both matrices
    for mat in (distances, durations):
        # diagonal must be exactly zero
        if any(mat[i][i] != 0 for i in range(num_points)):
            return None

        for i in range(num_points):
            for j in range(num_points):
                if i != j:
                    # off-diagonal must be positive
                    if mat[i][j] <= 0:
                        if mat[j][i] > 0:
                            mat[i][j] = mat[j][i]
                        else:
                            # Record this as an invalid pair if not already recorded
                            if (i, j) not in invalid_pairs:
                                invalid_pairs.append((i, j))

    return distances, durations, invalid_pairs


# -----------------------------------------------------------------------------------#
async def get_osrm_route(coords, order, avoid_zones: Iterable | None = None):
    """
    Get OSRM route with optional avoid zones processing.

    For multi-waypoint requests with avoid zones, uses segment-based alternatives:
    - Decomposes route into 2-coordinate segments
    - Requests alternatives for each segment
    - Recombines into complete route alternatives
    - Scores by avoid zone penalties

    Args:
        coords: List of all coordinate dicts
        order: Ordered indices for waypoint visitation
        avoid_zones: Optional list of avoid zone dicts with 'name' and 'coord' keys

    Returns:
        tuple: (route_data, ordered_coords)
    """
    ordered = [coords[ii] for ii in order]
    coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in ordered])

    # Check if we should use segment-based alternatives
    has_avoid_zones = avoid_zones and len(avoid_zones) > 0
    has_multiple_waypoints = len(ordered) > 2

    if has_avoid_zones and has_multiple_waypoints:
        logger.info(
            f"Multi-waypoint route with avoid zones: using segment-based alternatives "
            f"({len(ordered)} waypoints)"
        )

        try:
            # Use segment-based alternatives for multi-waypoint requests
            alternatives, error = await get_alternatives_for_multipoint_route(
                coordinates=ordered,
                request_osrm_fn=request_osrm,
                avoid_zones=avoid_zones,
                num_alternatives=ALTERNATIVES,
                max_routes=ALTERNATIVES,
            )

            if error:
                logger.warning(
                    f"Segment-based alternatives failed: {error}. Falling back to standard routing"
                )
            elif alternatives:
                logger.info(
                    f"Successfully generated {len(alternatives)} alternative routes via segment-based approach"
                )

                # Check if all alternatives cross avoid zones (penalty > 0)
                all_cross_zones = all(alt.get("penalty_score", 0) > 0 for alt in alternatives)
                
                if all_cross_zones and len(alternatives) > 0:
                    logger.info("All segment alternatives cross avoid zones, attempting zone-aware routing...")
                    
                    # Try zone-aware routing with waypoint insertion
                    try:
                        geojson = avoid_zones_to_geojson(avoid_zones)
                        polys, tree = load_spatial_index(geojson)
                        if polys:
                            zone_route = await find_route_around_zones(
                                start_coord=ordered[0],
                                waypoints=ordered[1:-1],
                                request_osrm_fn=request_osrm,
                                polygons=polys,
                                avoid_zones_list=avoid_zones,
                            )
                            
                            if zone_route and zone_route.get("geometry"):
                                logger.info("Zone-aware routing succeeded, using alternate path")
                                logger.debug(f"Zone-aware route: {len(zone_route.get('geometry', []))} coords, {zone_route.get('distance', 0):.0f}m")
                                
                                # Check if this route avoids zones better
                                intersection_data = check_route_intersections(
                                    zone_route["geometry"], polys, tree
                                )
                                logger.info(f"Zone-aware route intersection check: {intersection_data['intersection_count']} intersections, penalty {intersection_data['penalty_ratio']:.4f}")
                                
                                # If this route has lower penalty (less zone overlap), prioritize it
                                best_alt_penalty = alternatives[0].get("penalty_score", 999)
                                zone_aware_penalty = intersection_data["penalty_ratio"]
                                logger.info(f"Comparing penalties: zone-aware={zone_aware_penalty:.4f} vs best_alt={best_alt_penalty:.4f}")
                                
                                # Prioritize if it has significantly lower penalty (at least 10% improvement)
                                if zone_aware_penalty < best_alt_penalty * 0.9:
                                    logger.info(f"Zone-aware route has better penalty ({zone_aware_penalty:.4f} vs {best_alt_penalty:.4f}), prioritizing")
                                    alternatives.insert(0, {
                                        "geometry": {
                                            "type": "LineString",
                                            "coordinates": zone_route["geometry"]
                                        },
                                        "distance": zone_route.get("distance", 0),
                                        "duration": zone_route.get("duration", 0),
                                        "zone_intersections": intersection_data["intersection_count"],
                                        "penalty_score": intersection_data["penalty_ratio"],
                                    })
                    except Exception as zone_e:
                        logger.warning(f"Zone-aware routing failed: {zone_e}")
                
                # Convert segment-based routes to OSRM format
                osrm_routes = []
                for alt in alternatives:
                    osrm_route = {
                        "geometry": alt["geometry"],
                        "distance": alt["distance"],
                        "duration": alt["duration"],
                        "penalties": {
                            "zone_intersections": alt.get("zone_intersections", 0),
                            "penalty_score": alt.get("penalty_score", 0),
                        },
                    }
                    osrm_routes.append(osrm_route)

                data = {
                    "routes": osrm_routes,
                    "waypoints": [
                        {"name": waypoint.get("description", "")}
                        for waypoint in ordered
                    ],
                    "code": "Ok",
                }

                logger.info(f"Returning {len(osrm_routes)} routes with zone penalties")
                return data, ordered
        except Exception as seg_e:
            logger.warning(
                f"Segment-based alternatives failed: {seg_e}. Falling back to standard routing"
            )

    # Try local container first (priority order as requested)
    try:
        params = {
            "alternatives": ALTERNATIVES,
            "overview": "full",
            "geometries": "geojson",
        }
        data = await request_osrm(
            request_type="route",
            coordinates=coord_str,
            params=params,
        )
        logger.info("Successfully retrieved route from local container")
        logger.info(f"OSRM returned {len(data.get('routes', []))} routes")
        return data, ordered
    except Exception as container_e:
        logger.warning(
            f"Local container route failed: {container_e}. Trying public API"
        )

    # Try public API if local container failed or if too many points
    try:
        if len(ordered) > 100:
            raise ValueError("Too many points for public API")

        logger.info(f"Attempting public API route for {len(ordered)} points")
        params = {
            "alternatives": ALTERNATIVES,
            "overview": "full",
            "geometries": "geojson",
        }
        data = await request_osrm(
            request_type="route",
            coordinates=coord_str,
            params=params,
        )
        logger.info("Successfully retrieved route from public API")
    except HTTPException:
        logger.error("Public route API failed. Using fallback response")
        # Fallback: return a minimal valid response structure
        data = {
            "routes": [
                {
                    "geometry": {
                        "coordinates": [[c["lng"], c["lat"]] for c in ordered]
                    },
                    "duration": 0,
                    "distance": 0,
                }
            ],
            "waypoints": [{"name": ""} for _ in ordered],
        }

    # Update descriptions
    for ii, waypoint in enumerate(ordered):
        if not waypoint.get("description"):
            waypoint["description"] = data["waypoints"][ii].get("name", "")

    return data, ordered


# -----------------------------------------------------------------------------------#
def solve_open_tsp_from_matrix(distance_matrix):
    """
    Usa o 'truque do retorno grátis': zera custo para voltar ao depósito (coluna 0).
    Retorna a ordem dos índices dos nós visitados, começando em 0 e
    *sem* o retorno final ao 0.
    """
    n = len(distance_matrix)
    # Copia e zera custo de retornar ao depósito (coluna 0, exceto o próprio 0)
    dm = [row[:] for row in distance_matrix]
    for ii in range(1, n):
        dm[ii][0] = 0  # voltar ao depósito custa 0

    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 veículo, inicia no nó 0
    routing = pywrapcp.RoutingModel(manager)

    def cost_cb(from_index, to_index):
        ii = manager.IndexToNode(from_index)
        jj = manager.IndexToNode(to_index)
        return int(dm[ii][jj])

    transit_idx = routing.RegisterTransitCallback(cost_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # Estratégia inicial simples
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(params)
    if not solution:
        raise RuntimeError("OR-Tools não encontrou solução.")

    # Extrai a rota; o último nó será 0 (retorno grátis). Remova-o.
    order = []
    idx = routing.Start(0)
    while not routing.IsEnd(idx):
        order.append(manager.IndexToNode(idx))
        idx = solution.Value(routing.NextVar(idx))
    return order


# -----------------------------------------------------------------------------------#
def seconds_to_hms(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# -----------------------------------------------------------------------------------#
# DEBUG
# -----------------------------------------------------------------------------------#
if __name__ == "__main__":
    origin = {"lat": -23.55052, "lng": -46.57421}
    waypoints = [
        {"lat": -23.54785, "lng": -46.58325},
        {"lat": -23.55130, "lng": -46.57944},
    ]

    result = calculate_optimal_route(origin, waypoints)
    print(result)
