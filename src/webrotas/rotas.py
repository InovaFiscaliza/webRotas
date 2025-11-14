import math
from dataclasses import dataclass

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import webrotas.cache.bounding_boxes as cb
import webrotas.regions as rg
import webrotas.shapefiles as sf
from webrotas.api_routing import compute_bounding_box, calculate_optimal_route
from webrotas.api_elevation import enrich_waypoints_with_elevation


@dataclass
class UserData:
    OSMRport: int = 5000
    ssid: str | None = None


class RouteProcessor:
    """Processor for different route types (shortest, circle, grid, ordered).

    Encapsulates shared parameters and routing logic for various route generation strategies.
    """

    def __init__(
        self,
        current_request,
        session_id,
        origin,
        avoid_zones,
        criterion,
    ):
        """Initialize RouteProcessor with common routing parameters.

        Args:
            current_request: Request object to be updated with routing results
            session_id: Unique session identifier
            origin: Starting point coordinates (dict with 'lat' and 'lng')
            avoid_zones: List of zones to avoid in route calculation
            criterion: Routing criterion ('distance', 'time', etc.)
        """
        self.current_request = current_request
        self.session_id = session_id
        self.origin = origin
        self.avoid_zones = avoid_zones
        self.criterion = criterion

    def process_shortest(
        self,
        waypoints,
        location_limits=[],
        location_urban_areas=[],
    ):
        """Process shortest route between origin and waypoints.

        Args:
            waypoints: List of waypoints to visit
            location_limits: Optional city boundaries
            location_urban_areas: Optional urban areas information
        """
        routing_area, bounding_box, cache_id = compute_routing_area(
            self.avoid_zones, self.origin, waypoints
        )
        # si.PreparaServidorRoteamento(routing_area)

        origin, waypoints, paths, estimated_time, estimated_distance = (
            calculate_optimal_route(self.origin, waypoints, self.criterion, self.avoid_zones)
        )

        origin, waypoints = enrich_waypoints_with_elevation(origin, waypoints)

        self.current_request.update(
            {
                "session_id": self.session_id,
                "cache_id": cache_id,
                "routing_area": routing_area,
                "bounding_box": bounding_box,
                "avoid_zones": self.avoid_zones,
                "location_limits": location_limits,
                "location_urban_areas": location_urban_areas,
                "location_urban_communities": get_polyline_comunities(routing_area),
                "origin": origin,
                "waypoints": waypoints,
                "criterion": self.criterion,
                "paths": paths,
                "estimated_distance": estimated_distance,
                "estimated_time": estimated_time,
            }
        )

    def process_circle(
        self,
        center_point,
        radius_km,
        total_waypoints,
    ):
        """Process circle route around a center point.

        Args:
            center_point: Center point coordinates (dict with 'lat' and 'lng')
            radius_km: Radius in kilometers
            total_waypoints: Number of waypoints to generate
        """
        waypoints = self._generate_waypoints_in_radius(
            center_point, radius_km, total_waypoints
        )
        self.process_shortest(waypoints)

    def process_grid(
        self,
        city,
        state,
        scope,
        point_distance,
    ):
        """Process grid route within a city or urban area.

        Args:
            city: City name
            state: State code
            scope: Either "Location" (city boundaries) or "UrbanAreas"
            point_distance: Distance between grid points in meters
        """
        location_limits, location_urban_areas = get_areas_urbanas_cache(city, state)

        match scope:
            case "Location":
                waypoints = self._generate_waypoints_in_city(
                    location_limits, self.avoid_zones, point_distance, scope
                )
            case "UrbanAreas":
                waypoints = self._generate_waypoints_in_city(
                    location_urban_areas, self.avoid_zones, point_distance, scope
                )
            case _:
                raise ValueError(f'Invalid scope "{scope}"')

        self.process_shortest(
            waypoints,
            location_limits,
            location_urban_areas,
        )

    def process_ordered(
        self,
        cache_id,
        bounding_box,
        waypoints,
    ):
        """Process ordered route with predefined cache and bounding box.

        Args:
            cache_id: Cache identifier
            bounding_box: Predefined bounding box
            waypoints: List of waypoints to visit
        """
        # routing_area, bounding_box, cache_id = compute_routing_area(self.avoid_zones, self.origin, waypoints)
        # si.PreparaServidorRoteamento(routing_area)

        routing_area = []  # PENDENTE

        origin, waypoints, paths, estimated_time, estimated_distance = (
            calculate_optimal_route(self.origin, waypoints, self.criterion, self.avoid_zones)
        )
        origin, waypoints = enrich_waypoints_with_elevation(origin, waypoints)

        self.current_request.update(
            {
                "session_id": self.session_id,
                "cache_id": cache_id,
                "routing_area": routing_area,
                "bounding_box": bounding_box,
                "avoid_zones": self.avoid_zones,
                "origin": origin,
                "waypoints": waypoints,
                "criterion": self.criterion,
                "paths": paths,
                "estimated_distance": estimated_distance,
                "estimated_time": estimated_time,
            }
        )

    @staticmethod
    def _generate_waypoints_in_radius(center_point, radius_km, total_waypoints):
        """Generate waypoints arranged in a circle."""
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

    @staticmethod
    def _generate_waypoints_in_city(
        city_boundaries: list, avoid_zones: list, point_distance: int, scope: str
    ) -> list:
        """Generate waypoints arranged in a grid within city boundaries."""
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


def compute_routing_area(avoid_zones, origin, waypoints):
    coords = [origin] + waypoints
    bounding_box = compute_bounding_box(coords)

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
