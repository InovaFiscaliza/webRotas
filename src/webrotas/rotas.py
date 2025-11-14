import json
import math
import uuid
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import webrotas.regions as rg
import webrotas.shapefiles as sf
from webrotas.api_routing import compute_bounding_box, calculate_optimal_route
from webrotas.api_elevation import enrich_waypoints_with_elevation
from webrotas.config.server_hosts import get_webrotas_url
from webrotas.server_env import env


@dataclass
class UserData:
    OSMRport: int = 5000
    ssid: str | None = None


class RouteProcessor:
    """Processor for different route types (shortest, circle, grid, ordered).

    Encapsulates shared parameters and routing logic for various route generation strategies.
    Replaces RouteRequestManager with a more streamlined async-friendly design.
    """

    def __init__(
        self,
        session_id,
        origin,
        avoid_zones,
        criterion,
        request_data=None,
        route_id=None,
    ):
        """Initialize RouteProcessor with common routing parameters.

        Args:
            session_id: Unique session identifier
            origin: Starting point coordinates (dict with 'lat' and 'lng')
            avoid_zones: List of zones to avoid in route calculation
            criterion: Routing criterion ('distance', 'time', etc.)
            request_data: Original request data (for create_initial_route)
            route_id: Unique route identifier (auto-generated if not provided)
        """
        self.session_id = session_id
        self.origin = origin
        self.avoid_zones = avoid_zones
        self.criterion = criterion
        self.request = request_data
        self.route_id = route_id or str(uuid.uuid4())

        # Route result fields (populated during processing)
        self.routing_area = None
        self.bounding_box = None
        self.location_limits = None
        self.location_urban_areas = None
        self.location_urban_communities = None
        self.waypoints = None
        self.paths = None
        self.estimated_distance = None
        self.estimated_time = None

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
        routing_area, bounding_box = compute_routing_area(
            self.avoid_zones, self.origin, waypoints
        )
        # si.PreparaServidorRoteamento(routing_area)

        origin, waypoints, paths, estimated_time, estimated_distance = (
            calculate_optimal_route(self.origin, waypoints, self.criterion, self.avoid_zones)
        )

        origin, waypoints = enrich_waypoints_with_elevation(origin, waypoints)

        # Store results in instance for response generation
        self.routing_area = routing_area
        self.bounding_box = bounding_box
        self.location_limits = location_limits
        self.location_urban_areas = location_urban_areas
        self.location_urban_communities = get_polyline_comunities(routing_area)
        self.origin = origin
        self.waypoints = waypoints
        self.paths = paths
        self.estimated_distance = estimated_distance
        self.estimated_time = estimated_time

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

        # Store results in instance for response generation
        self.routing_area = routing_area
        self.bounding_box = bounding_box
        self.origin = origin
        self.waypoints = waypoints
        self.paths = paths
        self.estimated_distance = estimated_distance
        self.estimated_time = estimated_time

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

    def create_initial_route(self):
        """Generate initial route response with location and routing details."""
        initial_route = {
            "url": f"{get_webrotas_url(env.port)}/",
            "type": "initialRoute",
            "routing": [
                {
                    "request": self.request,
                    "response": {
                        "boundingBox": self.bounding_box,
                        "location": {
                            "limits": self.location_limits,
                            "urbanAreas": self.location_urban_areas,
                            "urbanCommunities": self.location_urban_communities,
                        },
                        "routes": [self.route_for_gui()],
                    },
                }
            ],
        }
        return json.dumps(initial_route, indent=4, ensure_ascii=False)

    def create_custom_route(self):
        """Generate custom route response."""
        custom_route = {"type": "customRoute", "route": self.route_for_gui()}
        return json.dumps(custom_route, indent=4, ensure_ascii=False)

    def route_for_gui(self):
        """Format route data for GUI consumption."""
        return {
            "routeId": self.route_id,
            "automatic": self.criterion != "ordered",
            "created": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "origin": self.origin,
            "waypoints": self.waypoints,
            "paths": self.paths,
            "estimatedDistance": self.estimated_distance,
            "estimatedTime": self.estimated_time,
        }

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

    return (routing_area, bounding_box)


# -----------------------------------------------------------------------------------#
def get_areas_urbanas_cache(city, state):
    """Fetch urban areas data for a city/state combination.
    
    Note: Cache has been removed as it's no longer necessary with async FastAPI.
    Data is fetched directly from shapefiles on each request.
    """
    polMunicipio = sf.GetBoundMunicipio(city, state)
    polMunicipioAreasUrbanizadas = sf.FiltrarAreasUrbanizadasPorMunicipio(
        city, state
    )
    return polMunicipio, polMunicipioAreasUrbanizadas


# -----------------------------------------------------------------------------------#
def get_polyline_comunities(regioes):
    """Fetch community polylines for a region.
    
    Note: Cache has been removed as it's no longer necessary with async FastAPI.
    Polylines are fetched directly from shapefiles on each request.
    """
    bounding_box = rg.extrair_bounding_box_de_regioes(regioes)
    polylinesComunidades = sf.FiltrarComunidadesBoundingBox(bounding_box)
    return polylinesComunidades
