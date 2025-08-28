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

# URLs do OSRM demo server
URL = {
    "table": lambda coord_str: f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration",
    "route": lambda coord_str: f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson",
}

# Bounding Box de Niterói (aproximado)
BBOX_NITEROI = {
    "min_lat": -22.933,
    "max_lat": -22.830,
    "min_lng": -43.150,
    "max_lng": -43.030,
}


# -----------------------------------------------------------------------------------#
def random_points_in_bbox(n_points, bbox):
    """Gera lista de pontos aleatórios dentro de um bounding box."""
    coords = []
    for _ in range(n_points):
        lat = random.uniform(bbox["min_lat"], bbox["max_lat"])
        lng = random.uniform(bbox["min_lng"], bbox["max_lng"])
        coords.append({"lat": lat, "lng": lng})
    return coords


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
def get_osrm_route(coords, order):
    """Calcula rota com polyline, preservando as descrições."""
    ordered = [coords[ii] for ii in order]
    coords_latlng = [(c["lat"], c["lng"]) for c in ordered]

    encoded = polyline.encode(coords_latlng, precision=5)
    coord_str = f"polyline({encoded})"


    req = requests.get(URL["route"](coord_str), timeout=10)
    req.raise_for_status()
    data = req.json()

    for ii, waypoint in enumerate(ordered):
        if not waypoint.get("description"):
            waypoint["description"] = data["waypoints"][ii].get("name", "")

    return data, ordered


# -----------------------------------------------------------------------------------#
if __name__ == "__main__":
    N = 500  # número de pontos para gerar
    coords = random_points_in_bbox(N, BBOX_NITEROI)

    print(f"Gerados {N} pontos aleatórios em Niterói:")

    # Testa matriz
    # t0 = time.time()
    # distances, durations = get_osrm_matrix(coords)
    # t1 = time.time()
    # print(f"\nMatriz OSRM (tempo: {t1 - t0:.2f}s):")
    # print("Distâncias:", distances)
    # print("Durações:", durations)

    # Testa rota
    order = list(range(N))  # ordem sequencial
    t0 = time.time()
    route_data, ordered = get_osrm_route(coords, order)
    t1 = time.time()
    print(f"\nRota OSRM (tempo: {t1 - t0:.2f}s):")
    print("Waypoints:", [wp["description"] for wp in ordered])
    print(
        "Resumo da rota:", route_data.get("routes", [{}])[0].get("distance", "N/A"), "m"
    )
