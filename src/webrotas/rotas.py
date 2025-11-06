import math
from dataclasses import dataclass

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import webrotas.cache.bounding_boxes as cb
import webrotas.regions as rg
import webrotas.shapefiles as sf
from webrotas import api_elevation, api_routing


@dataclass
class UserData:
    OSMRport: int = 5000
    ssid: str | None = None


def osrm_shortest(
    current_request,
    session_id,
    origin,
    waypoints,
    avoid_zones,
    criterion,
    location_limits=[],
    location_urban_areas=[],
):
    routing_area, bounding_box, cache_id = compute_routing_area(
        avoid_zones, origin, waypoints
    )
    # si.PreparaServidorRoteamento(routing_area)

    origin, waypoints, paths, estimated_time, estimated_distance = (
        api_routing.controller(origin, waypoints, criterion, avoid_zones)
    )
    origin, waypoints = api_elevation.controller(origin, waypoints)

    current_request.update(
        {
            "session_id": session_id,
            "cache_id": cache_id,
            "routing_area": routing_area,
            "bounding_box": bounding_box,
            "avoid_zones": avoid_zones,
            "location_limits": location_limits,
            "location_urban_areas": location_urban_areas,
            "location_urban_communities": get_polyline_comunities(routing_area),
            "origin": origin,
            "waypoints": waypoints,
            "criterion": criterion,
            "paths": paths,
            "estimated_distance": estimated_distance,
            "estimated_time": estimated_time,
        }
    )


# -----------------------------------------------------------------------------------#
def osrm_circle(
    current_request,
    session_id,
    origin,
    center_point,
    radius_km,
    total_waypoints,
    avoid_zones,
    criterion,
):
    ## <Função escopo local> ##
    def generate_waypoints_in_radius(center_point, radius_km, total_waypoints):
        R = 6371.0
        waypoints = []

        lat_rad = math.radians(center_point["lat"])
        lng_rad = math.radians(center_point["lng"])

        for ii in range(total_waypoints):
            angle = 2 * math.pi * ii / total_waypoints

            new_lat_rad = math.asin(
                math.sin(lat_rad) * math.cos(radius_km / R)
                + math.cos(lat_rad) * math.sin(radius_km / R) * math.cos(angle)
            )
            new_lon_rad = lng_rad + math.atan2(
                math.sin(angle) * math.sin(radius_km / R) * math.cos(lat_rad),
                math.cos(radius_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad),
            )

            new_lat = math.degrees(new_lat_rad)
            new_lon = math.degrees(new_lon_rad)
            waypoints.append(
                {
                    "lat": np.round(new_lat, 6),
                    "lng": np.round(new_lon, 6),
                    "description": "",
                }
            )

        return waypoints

    ## </Função escopo local> ##

    waypoints = generate_waypoints_in_radius(center_point, radius_km, total_waypoints)
    osrm_shortest(
        current_request, session_id, origin, waypoints, avoid_zones, criterion
    )


# -----------------------------------------------------------------------------------#
def osrm_grid(
    current_request,
    session_id,
    origin,
    city,
    state,
    scope,
    point_distance,
    avoid_zones,
    criterion,
):
    ## <Função escopo local> ##
    def generate_waypoints_in_city(
        city_boundaries: list, avoid_zones: list, point_distance: int
    ) -> list:
        city_polygon_list = []
        avoid_polygon_list = []

        for boundary in city_boundaries:
            city_polygon_list.append(
                Polygon([(float(lng), float(lat)) for lng, lat in boundary])
            )

        for zone in avoid_zones:
            """
                Na requisição .json, "avoid_zones" está uma lista de [lat, lng].
                Numa refatoração, transformá-la em uma lista de objetos.
            """
            avoid_polygon_list.append(
                Polygon([(float(lng), float(lat)) for lat, lng in zone["coord"]])
            )

        def meter_to_degree(lat_center, distance_m):
            lat_step = distance_m / 111_000
            lng_step = distance_m / (111_000 * np.cos(np.radians(lat_center)))
            return lng_step, lat_step

        lng_min, lat_min, lng_max, lat_max = unary_union(city_polygon_list).bounds
        lng_step, lat_step = meter_to_degree((lat_min + lat_max) / 2, point_distance)

        lng_range = np.arange(lng_min, lng_max, lng_step)
        lat_range = np.arange(lat_min, lat_max, lat_step)

        waypoints = []
        for lat in lat_range:
            for lng in lng_range:
                point = Point(lng, lat)
                if any(
                    city_polygon.contains(point) for city_polygon in city_polygon_list
                ):
                    inside_avoid = any(
                        zone.contains(point) for zone in avoid_polygon_list
                    )
                    if not inside_avoid:
                        waypoints.append(
                            {
                                "lat": np.round(lat, 6),
                                "lng": np.round(lng, 6),
                                "description": "",
                            }
                        )

        if not waypoints:
            raise ValueError(
                f'No waypoints found for scope "{scope}" with a point distance of {point_distance} meters.'
            )
        return waypoints

    ## </Função escopo local> ##

    location_limits, location_urban_areas = get_areas_urbanas_cache(city, state)

    match scope:
        case "Location":
            waypoints = generate_waypoints_in_city(
                location_limits, avoid_zones, point_distance
            )
        case "UrbanAreas":
            waypoints = generate_waypoints_in_city(
                location_urban_areas, avoid_zones, point_distance
            )
        case _:
            raise ValueError(f'Invalid scope "{scope}"')

    osrm_shortest(
        current_request,
        session_id,
        origin,
        waypoints,
        avoid_zones,
        criterion,
        location_limits,
        location_urban_areas,
    )


# -----------------------------------------------------------------------------------#
def osrm_ordered(
    current_request,
    session_id,
    origin,
    cache_id,
    bounding_box,
    waypoints,
    avoid_zones,
    criterion,
):
    # routing_area, bounding_box, cache_id = compute_routing_area(avoid_zones, origin, waypoints)
    # si.PreparaServidorRoteamento(routing_area)

    routing_area = []  # PENDENTE

    origin, waypoints, paths, estimated_time, estimated_distance = (
        api_routing.controller(origin, waypoints, criterion, avoid_zones)
    )
    origin, waypoints = api_elevation.controller(origin, waypoints)

    current_request.update(
        {
            "session_id": session_id,
            "cache_id": cache_id,
            "routing_area": routing_area,
            "bounding_box": bounding_box,
            "avoid_zones": avoid_zones,
            "origin": origin,
            "waypoints": waypoints,
            "criterion": criterion,
            "paths": paths,
            "estimated_distance": estimated_distance,
            "estimated_time": estimated_time,
        }
    )


# -----------------------------------------------------------------------------------#
def compute_routing_area(avoid_zones, origin, waypoints):
    ## <Função escopo local> ##
    def compute_bounding_box(origin, waypoints, padding_km=50):
        points = waypoints + [origin]
        lat_min = min(point["lat"] for point in points)
        lat_max = max(point["lat"] for point in points)
        lng_min = min(point["lng"] for point in points)
        lng_max = max(point["lng"] for point in points)

        lat_diff = padding_km / 111.0
        lng_diff = padding_km / (
            111.0 * math.cos(math.radians((lat_min + lat_max) / 2))
        )

        lat_min -= lat_diff
        lat_max += lat_diff
        lng_min -= lng_diff
        lng_max += lng_diff

        return (
            round(lat_min, 6),
            round(lat_max, 6),
            round(lng_min, 6),
            round(lng_max, 6),
        )

    ## </Função escopo local> ##

    lat_min, lat_max, lng_min, lng_max = compute_bounding_box(origin, waypoints)
    bounding_box = [
        [lat_max, lng_min],
        [lat_max, lng_max],
        [lat_min, lng_max],
        [lat_min, lng_min],
    ]

    routing_area = [{"name": "boundingBoxRegion", "coord": bounding_box}]

    for avoid_zone in avoid_zones:
        routing_area.append(
            {"name": avoid_zone["name"].replace(" ", "_"), "coord": avoid_zone["coord"]}
        )

    cached_routing_area, cache_id = cb.cCacheBoundingBox.get_cache(routing_area)
    if cached_routing_area is not None:
        routing_area = cached_routing_area

    return (routing_area, bounding_box, cache_id)


# -----------------------------------------------------------------------------------#
def get_areas_urbanas_cache(city, state):
    chave_regiao = {"city": city, "state": state}
    cache_polylines = cb.cCacheBoundingBox.areas_urbanas.get_polylines(chave_regiao)

    if not cache_polylines:
        polMunicipio = sf.GetBoundMunicipio(city, state)
        polMunicipioAreasUrbanizadas = sf.FiltrarAreasUrbanizadasPorMunicipio(
            city, state
        )
        cache_polylines = [
            f"{city}-{state}",
            polMunicipio,
            polMunicipioAreasUrbanizadas,
        ]
        cb.cCacheBoundingBox.areas_urbanas.add_polyline(chave_regiao, cache_polylines)

    else:
        polMunicipio = cache_polylines[1]
        polMunicipioAreasUrbanizadas = cache_polylines[2]

    return polMunicipio, polMunicipioAreasUrbanizadas


# -----------------------------------------------------------------------------------#
def get_polyline_comunities(regioes):
    bounding_box = rg.extrair_bounding_box_de_regioes(regioes)
    polylinesComunidades = cb.cCacheBoundingBox.comunidades_cache.get_polylines(regioes)

    if not polylinesComunidades:
        polylinesComunidades = sf.FiltrarComunidadesBoundingBox(bounding_box)
        cb.cCacheBoundingBox.comunidades_cache.add_polyline(
            regioes, polylinesComunidades
        )

    return polylinesComunidades
