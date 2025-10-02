import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from geopy.distance import geodesic

TIMEOUT = 10
URL = {
    "table":  lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route":  lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson"
}

#-----------------------------------------------------------------------------------#
def controller(origin, waypoints, criterion="distance"):
    coords = [origin] + waypoints

    try:
        distances, durations = get_osrm_matrix(coords)
    except (requests.exceptions.RequestException, ValueError, KeyError):
        distances, durations = get_osrm_matrix_from_local_container(coords)

    if not check_matrix_validity(coords, distances, durations):
        distances, durations = get_geodesic_matrix(coords, speed_kmh=40)

    if criterion in ["distance", "duration"]:
        matrix = distances if criterion == "distance" else durations
        order  = solve_open_tsp_from_matrix(matrix)
    else:
        order = list(range(len(coords)))

    route_json, ordered_coords = get_osrm_route(coords, order)
    paths = [list(reversed(path)) for path in route_json["routes"][0]["geometry"]["coordinates"]]

    estimated_sec = route_json["routes"][0]["duration"]
    estimated_m   = route_json["routes"][0]["distance"]

    return (
        ordered_coords[0],
        ordered_coords[1:], 
        paths, 
        seconds_to_hms(estimated_sec), 
        f"{round(estimated_m / 1000, 1)} km"
    )

#-----------------------------------------------------------------------------------#
def get_osrm_matrix(coords):
    coord_str = ";".join(f"{c['lng']},{c['lat']}" for c in coords)

    req = requests.get(URL["table"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()        

    return data["distances"], data["durations"]

#-----------------------------------------------------------------------------------#
def get_osrm_matrix_from_local_container(coords):
    # ToDo:
    # Estimar bounding box que atende a rota, verificar se há container
    # local ativo para essa área. Caso contrário, abre-se um novo container.
    # O erro não pode vazar para o cliente porque a chamada desse método se
    # deu no except do método principal.

    data = {
        "distances": [],
        "durations": []
    }    

    return data["distances"], data["durations"]

# -----------------------------------------------------------------------------------#
def get_geodesic_matrix(coords, speed_kmh=40):
    num_points = len(coords)
    distances = [[0.0] * num_points for _ in range(num_points)]

    for ii in range(num_points):
        for jj in range(num_points):
            if ii != jj:
                p1 = (coords[ii]["lat"], coords[ii]["lng"])
                p2 = (coords[jj]["lat"], coords[jj]["lng"])
                distances[ii][jj] = geodesic(p1, p2).meters
    
    durations = [[(dist / speed_kmh) * 3600 for dist in row] for row in distances]

    return distances, durations

#-----------------------------------------------------------------------------------#
def check_matrix_validity(coords, distances, durations):
    num_points = len(coords)
    if distances is None or durations is None:
        return False
    
    if not (len(distances) == len(durations) == num_points):
        return False

    for ii in range(num_points):
        if not (len(distances[ii]) == len(durations[ii]) == num_points):
            return False
        
    for ii in range(num_points):
        for jj in range(num_points):
            d, t = distances[ii][jj], durations[ii][jj]
            if ii == jj:
                if not (d == 0 and t == 0):
                    return False
            else:
                if d <= 0 or t <= 0:
                    return False

    return True

#-----------------------------------------------------------------------------------#
def get_osrm_route(coords, order):
    ordered   = [coords[ii] for ii in order]
    coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in ordered])

    req = requests.get(URL["route"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    for ii, waypoint in enumerate(ordered):
        if not waypoint.get("description"):
            waypoint["description"] = data["waypoints"][ii].get("name", "")

    return data, ordered

#-----------------------------------------------------------------------------------#
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
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

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

#-----------------------------------------------------------------------------------#
def seconds_to_hms(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

#-----------------------------------------------------------------------------------#
# DEBUG
#-----------------------------------------------------------------------------------#
if __name__ == "__main__":
    origin    = {"lat": -23.55052, "lng": -46.57421}
    waypoints = [
        {"lat": -23.54785, "lng": -46.58325},
        {"lat": -23.55130, "lng": -46.57944},
    ]

    result = controller(origin, waypoints)
    print(result)