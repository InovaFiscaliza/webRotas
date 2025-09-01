import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import numpy as np
import polyline
from geopy.distance import geodesic

MAX_OSRM_MATRIX_POINTS = 100  # limite do servidor OSRM (ajuste se seu container suportar mais)
MAX_OSRM_POINTS = 450  # limite do servidor OSRM (ajuste se seu container suportar mais)
OSRM_URL = "http://router.project-osrm.org/"
TIMEOUT = 10
URL = {
    "table": lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}


# -----------------------------------------------------------------------------------#
def controller(origin, waypoints, criterion="distance"):
    coords = [origin] + waypoints

    n_points = len(coords)
    # verifica se ultrapassa o limite de pontos
    if n_points > MAX_OSRM_MATRIX_POINTS:
        distances, durations = get_geodesic_matrix(coords)
    else:
        try:
            distances, durations = get_osrm_matrix(coords)
        except Exception as e:
            distances, durations = get_osrm_matrix_podman(coords)

    if criterion in ["distance", "duration"]:
        matrix = distances if criterion == "distance" else durations
        order = solve_open_tsp_from_matrix(matrix)
    else:
        order = list(range(len(coords)))

    

    if n_points > MAX_OSRM_POINTS:
       route_json, ordered_coords = get_osrm_route_podman(coords, order)
    else:
        try:
            route_json, ordered_coords = get_osrm_route(coords, order)
        except Exception as e:
            route_json, ordered_coords = get_osrm_route_podman(coords, order)
    
    
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
def check_osrm_status():
    """Faz uma chamada de teste ao OSRM e verifica se está operacional."""
    try:
        # Chamando a API de status simples (table com 2 pontos de teste)
        test_coords = "-43.12,-22.91;-43.13,-22.92"  # pontos em Niterói, RJ
        url = f"{OSRM_URL}table/v1/driving/{test_coords}?annotations=distance,duration"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Verifica se a resposta tem as chaves esperadas
        if "distances" in data and "durations" in data:
            return True, "OSRM está online e operacional."
        else:
            return False, "OSRM respondeu, mas dados esperados não encontrados."

    except requests.exceptions.RequestException as e:
        return False, f"Erro ao acessar OSRM: {e}"

# -----------------------------------------------------------------------------------#
def get_osrm_matrix(coords):
    """Gera matriz de distâncias e durações via OSRM, usando polyline."""
    coords_latlng = [(c["lat"], c["lng"]) for c in coords]
    encoded = polyline.encode(coords_latlng, precision=5)
    coord_str = f"polyline({encoded})"

    req = requests.get(URL["table"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    return data["distances"], data["durations"]

# -----------------------------------------------------------------------------------#
def get_geodesic_matrix(coords):
    """
    Gera matriz de distâncias geodésicas (em km) entre os pontos.
    coords: lista de dicts {'lat': float, 'lng': float}
    """
    n = len(coords)
    distances = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                p1 = (coords[i]["lat"], coords[i]["lng"])
                p2 = (coords[j]["lat"], coords[j]["lng"])
                distances[i][j] = geodesic(p1, p2).km

    return distances, distances  # retorna distâncias em km como durações fictícias

# -----------------------------------------------------------------------------------#
def get_osrm_matrix_podman(coords):
    raise NotImplementedError("Função não implementada. get_osrm_matrix_podman")
    return


# -----------------------------------------------------------------------------------#
def get_osrm_route(coords, order):
    """Calcula rota com polyline, preservando as descrições."""
    ordered = [coords[ii] for ii in order]
    coords_latlng = [(c["lat"], c["lng"]) for c in ordered]

    encoded = polyline.encode(coords_latlng, precision=5)
    coord_str = f"polyline({encoded})"

    print(URL["route"](coord_str))
    req = requests.get(URL["route"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    for ii, waypoint in enumerate(ordered):
        if not waypoint.get("description"):
            waypoint["description"] = data["waypoints"][ii].get("name", "")

    return data, ordered
# -----------------------------------------------------------------------------------#
def get_osrm_route_podman(coords, order):
    raise NotImplementedError("Função não implementada. get_osrm_route_podman")
    return

# -----------------------------------------------------------------------------#
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
