import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import numpy as np
import polyline
from geopy.distance import geodesic
import wlog as wl
import cache_bounding_box as cb


MAX_OSRM_MATRIX_POINTS = 100  # limite do servidor OSRM (ajuste se seu container suportar mais)
MAX_OSRM_POINTS = 450  # limite do servidor OSRM (ajuste se seu container suportar mais)
OSRM_URL = "http://router.project-osrm.org/"
TIMEOUT = 10
URL = {
    "table": lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}


# -----------------------------------------------------------------------------------#
def controller(origin, waypoints, criterion="distance", bounding_box=[], avoid_zones=[]):
    coords = [origin] + waypoints

    n_points = len(coords)
    # verifica se ultrapassa o limite de pontos
    if n_points > MAX_OSRM_MATRIX_POINTS:
        distances, durations = get_geodesic_matrix(coords)
    else:
        try:
            distances, durations = get_osrm_matrix(coords)
        except Exception as e:
            distances, durations = get_osrm_matrix_podman(coords, bounding_box, avoid_zones)

    if criterion in ["distance", "duration"]:
        matrix = distances if criterion == "distance" else durations
        order = solve_open_tsp_from_matrix(matrix)
    else:
        order = list(range(len(coords)))

    

    if n_points > MAX_OSRM_POINTS:
       route_json, ordered_coords = get_osrm_route_podman(coords, order, bounding_box, avoid_zones)
    else:
        try:
            route_json, ordered_coords = get_osrm_route(coords, order)
        except Exception as e:
            route_json, ordered_coords = get_osrm_route_podman(coords, order, bounding_box, avoid_zones)
    
    
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
    """Gera matriz de distâncias e durações via OSRM, sem usar polyline.
    
    Levanta exceção se as primeiras distâncias vierem zeradas (indicando erro).
    """
    # OSRM espera no formato lng,lat (atenção à ordem!)
    coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in coords])
    url = URL["table"](coord_str)
    req = requests.get(url, timeout=10)
    req.raise_for_status()
    data = req.json()

    distances = data.get("distances")
    durations = data.get("durations")

    if not distances:
        raise ValueError("OSRM não retornou matriz de distâncias.")

    # Limita checagem às 10 primeiras linhas/colunas
    n_check = min(10, len(distances))
    all_zero = True
    for i in range(n_check):
        for j in range(n_check):
            if i != j and distances[i][j] > 0:
                all_zero = False
                break
        if not all_zero:
            break

    if all_zero:
        raise ValueError("As primeiras 10 distâncias retornaram zeradas. Verifique coordenadas ou OSRM.")

    return distances, durations

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
def get_osrm_matrix_podman(coords, bounding_box, avoid_zones):



    # Coordenadas de início e fim
    start_coords = (start_lat, start_lon)
    end_coords = (end_lat, end_lon)

    if ServerTec == "OSMR":
        # URL da solicitação ao servidor OSMR
        url = f"http://localhost:{UserData.OSMRport}/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline&steps=true"

    # http://localhost:50000/route/v1/driving/-51.512533967708904,-29.972345983755194;-51.72406122295204,-30.03608928259163?overview=full&geometries=polyline&steps=true

    wl.wlog(url, level="debug")
    if porta_disponivel("localhost", UserData.OSMRport):
        response = requests.get(url)
        data = response.json()
        if (
            response.status_code == 200
            and "routes" in data
            and (route_failure(data) == False)
        ):
            cb.cCacheBoundingBox.route_cache_set(
                start_lat, start_lon, end_lat, end_lon, response
            )
            return response

    wl.wlog(
        f"GetRouteFromServer erro na solicitacao - rota pedida nao existe ou servidor fora do ar ",
        level="debug",
    )
    # cb.cCacheBoundingBox.find_server_for_this_route(start_lat, start_lon, end_lat, end_lon)
    # Tenta buscar do cache
    # region = cb.cCacheBoundingBox.find_server_for_this_route(32.324276, -100.546875, 31.802893, -95.625000)
    # region2 = cb.cCacheBoundingBox.find_server_for_this_route(-29.747937866768677, -52.23053107185985,-29.795851462719526, -50.850979532029115)
    responseTmp = si.start_or_find_server_for_this_route(
        start_lat, start_lon, end_lat, end_lon
    )
    if responseTmp == False:
        wl.wlog(f"Não temos cache para a rota")
        return None
    return get_osrm_matrix_podman(coords, bounding_box, avoid_zones)   
    
    raise NotImplementedError("Função não implementada. get_osrm_matrix_podman")
    return


# -----------------------------------------------------------------------------------#
def get_osrm_route(coords, order):
    """Calcula rota no OSRM sem usar polyline, preservando as descrições."""
    # Reordena os pontos conforme 'order'
    ordered = [coords[ii] for ii in order]

    # Monta string no formato lng,lat;lng,lat;...
    coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in ordered])
    url = URL["route"](coord_str)
    req = requests.get(url, timeout=10)
    req.raise_for_status()
    data = req.json()

    # Preenche descrições ausentes
    for ii, waypoint in enumerate(ordered):
        if not waypoint.get("description"):
            waypoint["description"] = data["waypoints"][ii].get("name", "")

    return data, ordered

# -----------------------------------------------------------------------------------#
def get_osrm_route_podman(coords, order, bounding_box, avoid_zones):
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
