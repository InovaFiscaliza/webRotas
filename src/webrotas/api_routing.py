import math
import socket
from typing import List, Tuple, Iterable

import requests
from geopy.distance import geodesic
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from webrotas.routing_servers_interface import PreparaServidorRoteamento, UserData
from webrotas.config.logging_config import get_logger
from webrotas.iterative_matrix_builder import IterativeMatrixBuilder

# Initialize logging at module level
logger = get_logger(__name__)


TIMEOUT = 10
URL = {
    "table": lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}


# -----------------------------------------------------------------------------------#
def controller(
    origin, waypoints, criterion: str = "distance", avoid_zones: Iterable | None = None
):
    coords = [origin] + waypoints
    use_container = False

    # Check if we should use local container due to limitations
    if len(coords) > 100:
        logger.info(
            f"Too many points ({len(coords)}), using local container or iterative matrix"
        )
        use_container = True

    if avoid_zones is not None and len(avoid_zones) > 0:
        logger.info(
            f"Exclusion zones present ({len(avoid_zones)}), using local container"
        )
        use_container = True

    if use_container:
        # Use local container directly
        try:
            distances, durations = get_osrm_matrix_from_local_container(coords)
        except Exception as e:
            if avoid_zones is None:
                logger.error(
                    f"Local container failed: {e}. 🟢 NO Avoidance Zones Present. Trying iterative matrix builder",
                    exc_info=True,
                )
                try:
                    distances, durations = get_osrm_matrix_iterative(coords)
                except Exception as iterative_e:
                    logger.warning(
                        f"Iterative matrix builder also failed: {iterative_e}. Using geodesic calculation"
                    )
                    distances, durations = get_geodesic_matrix(coords, speed_kmh=40)

            else:
                logger.error(
                    f"Local container failed: {e}. 🚫 Avoidance Zones present. Using geodesic calculation",
                    exc_info=True,
                )
                distances, durations = get_geodesic_matrix(coords, speed_kmh=40)
    else:
        # Try public API first
        try:
            distances, durations = get_osrm_matrix(coords)
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            logger.error(
                f"Public API failed: {e}. Trying local container", exc_info=True
            )
            try:
                distances, durations = get_osrm_matrix_from_local_container(coords)
            except Exception as container_e:
                logger.warning(
                    f"Local container also failed: {container_e}. Trying iterative matrix builder"
                )
                try:
                    distances, durations = get_osrm_matrix_iterative(coords)
                except Exception as iterative_e:
                    logger.warning(
                        f"Iterative matrix builder also failed: {iterative_e}. Using geodesic calculation"
                    )
                    distances, durations = get_geodesic_matrix(coords, speed_kmh=40)

    mat = validate_matrix(coords, distances, durations)

    if mat is None:
        logger.error("Matrix validation failed, falling back to geodesic calculation")
        distances, durations = get_geodesic_matrix(coords, speed_kmh=40)
    elif len(mat) == 3:
        # Invalid pairs found, only calculate geodesic for those
        distances, durations, invalid_pairs = mat
        logger.warning(
            f"Found {len(invalid_pairs)} invalid pairs, calculating geodesic only for those"
        )

        geodesic_distances, geodesic_durations = get_geodesic_matrix(
            coords, speed_kmh=40, invalid_pairs=invalid_pairs
        )

        # Merge geodesic values into the existing matrices
        for ii, jj in invalid_pairs:
            distances[ii][jj] = geodesic_distances[ii][jj]
            durations[ii][jj] = geodesic_durations[ii][jj]
    else:
        distances, durations = mat

    if criterion in ["distance", "duration"]:
        matrix = distances if criterion == "distance" else durations
        order = solve_open_tsp_from_matrix(matrix)
    else:
        order = list(range(len(coords)))

    route_json, ordered_coords = get_osrm_route(coords, order)
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


# -----------------------------------------------------------------------------------#
def get_osrm_matrix(coords):
    coord_str = ";".join(f"{c['lng']},{c['lat']}" for c in coords)

    req = requests.get(URL["table"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    return data["distances"], data["durations"]


# -----------------------------------------------------------------------------------#
def is_port_available(host="localhost", port=5000, timeout=10):
    """
    Check if a container is available on the specified port.

    Args:
        host (str): The host to check (default: localhost)
        port (int): The port to check (default: 5000)
        timeout (int): Connection timeout in seconds (default: 3)

    Returns:
        bool: True if port is available and responding, False otherwise
    """
    try:
        # First check if port is open
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result != 0:
                # Port is not open
                return False

        # Port is open, now check if OSRM is responding
        try:
            response = requests.get(f"http://{host}:{port}/health", timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            # Port is open but OSRM is not responding properly
            return False

    except Exception:
        return False


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


# -----------------------------------------------------------------------------------#
def get_osrm_matrix_from_local_container(coords):
    """
    Get distance and duration matrix from local OSRM container.

    This function:
    1. Checks if port 5000 is available and responding
    2. If not available, immediately raises exception to fallback to iterative method
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
    # First check if container is available on port 5000
    # Use 'osrm' hostname for Docker network connectivity
    if not is_port_available("osrm", 5000):
        raise Exception(
            "OSRM container not available on port 5000 - falling back to iterative method"
        )

    logger.info(
        "OSRM container verified available on port 5000, proceeding with local container request"
    )

    try:
        # Extract bounding box from coordinates
        if not coords or len(coords) < 2:
            raise ValueError("Need at least 2 coordinates for routing")

        # Calculate bounding box with padding for routing
        lats = [c["lat"] for c in coords]
        lngs = [c["lng"] for c in coords]

        lat_min, lat_max = min(lats), max(lats)
        lng_min, lng_max = min(lngs), max(lngs)

        # Add padding for routing (50km as in web_rotas.py)
        padding_km = 50
        lat_diff = padding_km / 111.0  # Approximately 1 degree = 111 km
        lng_diff = padding_km / (
            111.0 * math.cos(math.radians((lat_min + lat_max) / 2))
        )

        lat_min -= lat_diff
        lat_max += lat_diff
        lng_min -= lng_diff
        lng_max += lng_diff

        # Create routing area for container management
        bounding_box = [
            [lat_max, lng_min],
            [lat_max, lng_max],
            [lat_min, lng_max],
            [lat_min, lng_min],
        ]

        routing_area = [{"name": "boundingBoxRegion", "coord": bounding_box}]

        # Set up user data for container interface
        if not hasattr(UserData, "ssid") or UserData.ssid is None:
            import uuid

            UserData.ssid = str(uuid.uuid4())[:8]

        # Try to prepare the routing server
        PreparaServidorRoteamento(routing_area)

        # Check if server is running
        if not UserData.OSMRport:
            raise Exception("Failed to start OSRM container - no port assigned")

        # Make request to local container
        coord_str = ";".join(f"{c['lng']},{c['lat']}" for c in coords)
        # Use 'osrm' hostname for Docker network connectivity instead of localhost
        local_url = f"http://osrm:{UserData.OSMRport}/table/v1/driving/{coord_str}?annotations=distance,duration"

        logger.debug(f"Making request to local OSRM: {local_url}")

        # Use longer timeout for local container as it might need to start up
        response = requests.get(local_url, timeout=60)
        response.raise_for_status()

        data = response.json()

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
) -> Tuple[List[float], List[float]] | None:
    num_points = len(coords)
    if distances is None or durations is None:
        return False

    # quick shape checks
    if not (len(distances) == len(durations) == num_points):
        return False
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
            return False

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

    # If there are invalid pairs, return them along with the matrices
    if invalid_pairs:
        return distances, durations, invalid_pairs

    return distances, durations


# -----------------------------------------------------------------------------------#
def get_osrm_route(coords, order):
    ordered = [coords[ii] for ii in order]
    coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in ordered])

    # Try public API first
    try:
        if len(ordered) > 100:
            raise ValueError("Too many points for public API")

        req = requests.get(URL["route"](coord_str), timeout=10)
        req.raise_for_status()
        data = req.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.warning(f"Public route API failed: {e}. Trying local container")
    # Try local container
    try:
        if not UserData.OSMRport:
            raise Exception("No local OSRM container available")

        local_url = f"http://localhost:{UserData.OSMRport}/route/v1/driving/{coord_str}?overview=full&geometries=geojson"
        req = requests.get(local_url, timeout=30)
        req.raise_for_status()
        data = req.json()
    except Exception as container_e:
        logger.error(f"Local container route also failed: {container_e}")
        # Return a minimal valid response structure
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
    # idx agora é End(0) (que corresponde ao depósito 0). Remover retorno:
    if order and order[-1] != 0:
        # Se por alguma razão não voltou para 0 (não deve acontecer nesse setup), mantemos.
        pass
    else:
        # Garante sequência sem o retorno final ao 0.
        # A sequência atual termina no penúltimo nó visitado.
        # Não adicionamos o 0 final.
        pass

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

    result = controller(origin, waypoints)
    print(result)
