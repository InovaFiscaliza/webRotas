#!/usr/bin/env python3
"""
Programa de teste para rotinas OSRM (matrix e route) usando polyline.
- Gera pontos aleatórios dentro de um bounding box de Niterói (RJ).
- Mede o tempo de resposta das rotinas.
"""

import requests
import polyline
import random
import time
from geopy.distance import geodesic

# URLs do OSRM demo server
URL = {
    "table": lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}

# URLs do OSRM demo server
URL = {
    "table": lambda coord_str: f"http://localhost:50000/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://localhost:50000/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}

# Bounding Box de Niterói (aproximado)
BBOX_NITEROI = {
    "min_lat": -22.933,
    "max_lat": -22.830,
    "min_lng": -43.150,
    "max_lng": -43.030,
}

# Bounding Box de Salvador (aproximado)
BBOX_SALVADOR = {
    "min_lat": -13.050,
    "max_lat": -12.850,
    "min_lng": -38.600,
    "max_lng": -38.400,
}


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
def random_points_in_bbox(n_points, bbox):
    """Gera lista de pontos aleatórios dentro de um bounding box."""
    coords = []
    for _ in range(n_points):
        lat = random.uniform(bbox["min_lat"], bbox["max_lat"])
        lng = random.uniform(bbox["min_lng"], bbox["max_lng"])
        coords.append({"lat": lat, "lng": lng})
    return coords


# Polyline Salvador para testar no OSRM
# http://router.project-osrm.org/table/v1/driving/polyline(xqfnA`kuiFldCnbL?suA?uuA?suA?suAosApyI?suA?uuA?suA?suA?suAmsApyI?uuA?suA?suA?suA?uuA?suAmsAzfO?uuA?suA?suA?suA?uuA?glDosAxfO?suA?suA?suA?uuA?qyI?suA?suAmsA`x\\?uuA?suA?suA?suA?uuA?suA?suA?suA?uuA?suA?glDosAtn_@?ilD?suA?suA?uuA?suA?suAmsAdpL?suA?suA?uuA?suA?glD?ilD?suA?suA?suAmsA~w\\?suA?suA?uuA?suA?suA?suA?ilD?suAosAvjW?}bG?suA?suA?suA?uuAmsAzfO?}bG?qyImsAn}Q?ilD?yfOosAbtT?{fO?suA?suAmsAvjW)?annotations=distance,duration


# -----------------------------------------------------------------------------------#
def get_osrm_matrix(coords):
    """Gera matriz de distâncias e durações via OSRM, usando polyline."""
    coords_latlng = [(c["lat"], c["lng"]) for c in coords]
    encoded = polyline.encode(coords_latlng, precision=5)
    encoded =  quote(encoded, safe="")  # safe="" garante que tudo será codificado
    coord_str = f"polyline({encoded})"

    req = requests.get(URL["table"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    return data["distances"], data["durations"]


# -----------------------------------------------------------------------------------#
from urllib.parse import quote
def get_osrm_route(coords, order):
    """Calcula rota com polyline, preservando as descrições."""
    ordered = [coords[ii] for ii in order]
    coords_latlng = [(c["lat"], c["lng"]) for c in ordered]

    encoded = polyline.encode(coords_latlng, precision=5)
    encoded =  quote(encoded, safe="")  # safe="" garante que tudo será codificado
    
    coord_str = f"polyline({encoded})"

    print(URL["route"](coord_str))
    req = requests.get(URL["route"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    for ii, waypoint in enumerate(ordered):
        if not waypoint.get("description"):
            waypoint["description"] = data["waypoints"][ii].get("name", "")

    return data, ordered


# -----------------------------------------------------------------------------#
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


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


import json


# -----------------------------------------------------------------------------------#
def save_route_leaflet(route_data, ordered, filename="mapa.html"):
    """
    Gera um arquivo HTML com Leaflet mostrando a rota e os waypoints numerados.
    route_data: dict retornado do OSRM
    ordered: lista de coordenadas [{'lat': float, 'lng': float, 'description': str}]
    filename: nome do arquivo HTML de saída
    """
    # Extrai a geometria da rota (GeoJSON)
    geometry = route_data["routes"][0]["geometry"]

    # Converte waypoints em JSON para uso no JS
    waypoints_js = json.dumps(
        [
            {
                "lat": wp["lat"],
                "lng": wp["lng"],
                "desc": wp.get("description", ""),
                "num": i + 1,
            }
            for i, wp in enumerate(ordered)
        ],
        ensure_ascii=False,
    )

    # HTML com Leaflet
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Mapa da Rota</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
</head>
<body style="margin:0; padding:0;">
<div id="map" style="width: 100%; height: 100vh;"></div>
<script>
    // Inicializa o mapa
    var map = L.map('map');

    // Tile layer (OpenStreetMap)
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    // Adiciona a rota (GeoJSON)
    var route = {json.dumps(geometry)};
    var routeLayer = L.geoJSON(route).addTo(map);

    // Ajusta zoom para caber a rota
    map.fitBounds(routeLayer.getBounds());

    // Waypoints
    var waypoints = {waypoints_js};
    waypoints.forEach(function(wp) {{
        var marker = L.marker([wp.lat, wp.lng]).addTo(map);
        marker.bindPopup("<b>Ponto " + wp.num + "</b><br>" + wp.desc);
        marker.bindTooltip(wp.num.toString(), {{permanent: true, direction: "top"}});
    }});
</script>
</body>
</html>
"""

    # Salva arquivo
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Arquivo salvo: {filename}")


# -----------------------------------------------------------------------------------#
if __name__ == "__main__":
    N = 450  # número de pontos para gerar
    # coords = random_points_in_bbox(N, BBOX_NITEROI)
    coords = random_points_in_bbox(N, BBOX_SALVADOR)

    print(f"Gerados {N} pontos aleatórios em Salvador:")

    # Testa matriz
    # t0 = time.time()
    # distances, durations = get_osrm_matrix(coords)
    # t1 = time.time()
    # print(f"\nMatriz OSRM (tempo: {t1 - t0:.2f}s):")
    # print("Distâncias:", distances)
    # print("Durações:", durations)

    # Testa rota
    distances, durations = get_geodesic_matrix(coords)
    matrix = distances
    order = solve_open_tsp_from_matrix(matrix)
    # order = list(range(N))  # ordem sequencial

    # Ponto fixo em São Paulo
    sp_point = {
        "lat": -23.55052,
        "lng": -46.633308,
        "description": "São Paulo - Marco Zero",
    }

    # Insere no início da lista
    coords.insert(0, sp_point)

    # Garante que São Paulo (índice 0) fique como inicial
    idx = order.index(0)
    order = order[idx:] + order[:idx]

    t0 = time.time()
    route_data, ordered = get_osrm_route(coords, order)
    t1 = time.time()
    print(f"\nRota OSRM (tempo: {t1 - t0:.2f}s):")
    print("Waypoints:", [wp["description"] for wp in ordered])
    print(
        "Resumo da rota:", route_data.get("routes", [{}])[0].get("distance", "N/A"), "m"
    )

    save_route_leaflet(route_data, ordered, filename="mapa.html")
