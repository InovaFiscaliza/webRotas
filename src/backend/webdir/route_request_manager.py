#!/usr/bin/env python3
""" """

import json
from datetime import datetime
import uuid
from server_env import env

class RouteRequestManager:
    in_progress_requests = []

    def __init__(self, data=None, route_id=None):
        self.reset()
        self.request  = data
        self.route_id = route_id        

    def reset(self):
        self.request = None

        self.session_id = None
        self.cache_id = None
        self.route_id = None

        self.osrm_port = None

        self.routing_area = None
        self.bounding_box = None
        self.avoid_zones = None
        
        self.location_limits = None
        self.location_urban_areas = None
        self.location_urban_communities = None

        self.origin = None
        self.waypoints = None
        self.paths = None

        self.estimated_distance = None
        self.estimated_time = None

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def process_request(cls, request_type, data):
        match request_type:
            case "shortest" | "circle" | "grid":
                route_id    = str(uuid.uuid4())

                new_request = cls(data, route_id)
                cls.in_progress_requests.append(new_request)
                return new_request, True

            case "ordered":
                route_id    = data["route_id"]

                old_request = cls.find_by_route_id(route_id)
                if old_request:
                    return old_request, False
                
                new_request = cls(data, route_id)
                cls.in_progress_requests.append(new_request)
                return new_request, True

            case _:
                raise ValueError(f"Unknown request type: {request_type}")
            
    @classmethod
    def find_by_route_id(cls, route_id):
        return next((req for req in cls.in_progress_requests if req.route_id == route_id), None)

    def create_initial_route(self):
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        waypoints = self.gerar_waypoints(self.pontosvisitaDados)
        self.estimated_distance = round(self.estimated_distance / 1000, 1)

        # Round coordinates in waypoints_route
        rounded_paths = []
        if self.waypoints_route:
            for path in self.waypoints_route:
                rounded_path = []
                for coord in path:
                    rounded_path.append(self.round_coords(coord))
                rounded_paths.append(rounded_path)

        # Round coordinates in bounding_box
        rounded_bounding_box = []
        if self.bounding_box:
            for coord in self.bounding_box:
                rounded_bounding_box.append(self.round_coords(coord))

        # Round coordinates in limits
        rounded_limits = []
        if self.limits:
            for limit_group in self.limits:
                rounded_group = []
                for coord in limit_group:
                    rounded_group.append(self.round_coords(coord))
                rounded_limits.append(rounded_group)

        # Round coordinates in urbanAreas
        rounded_urban_areas = []
        if self.urbanAreas:
            for area in self.urbanAreas:
                rounded_area = []
                for coord in area:
                    rounded_area.append(self.round_coords(coord))
                rounded_urban_areas.append(rounded_area)

        routes_buf = [
            {
                "routeId": self.route_id if self.route_id is not None else str(uuid.uuid4()),
                "automatic": True,
                "created": f"{data}",
                "origin": {
                    "lat": round(float(self.pontoinicial[0]), 6),
                    "lng": round(float(self.pontoinicial[1]), 6),
                    "elevation": -9999, # Precisa pesquisar essa altitude
                    "description": f"{self.pontoinicial[2]}",
                },
                "waypoints": waypoints,
                "paths": rounded_paths,
                "estimatedDistance": self.estimated_distance,
                "estimatedTime": self.estimated_time,
            }
        ]

        estrutura = {
            "url": f"http://127.0.0.1:{env.port}/",
            "routing": [
                {
                    "request": self.requisition_data,
                    "response": {
                        "cacheId": f"{self.cache_id}",
                        "boundingBox": rounded_bounding_box,
                        "location": {
                            "limits": rounded_limits,
                            "urbanAreas": rounded_urban_areas,
                            "urbanCommunities": self.jsonComunities,
                        },
                        "routes": routes_buf,
                    },
                }
            ],
        }

        json_formatado = json.dumps(estrutura, indent=4, ensure_ascii=False)
        return json_formatado
    
    def create_custom_route(self):
        waypoints = self.gerar_waypoints(self.pontosvisitaDados)
        self.estimated_distance = round(self.estimated_distance / 1000, 1)

        routes_buf = {
            "routeId": self.route_id,
            "origin": self.origin,
            "waypoints": self.waypoints,
            "neededPaths": [],
            "estimatedDistance": self.estimated_distance,
            "estimatedTime": self.estimated_time
        }

        response = json.dumps(routes_buf, indent=4, ensure_ascii=False)
        return response