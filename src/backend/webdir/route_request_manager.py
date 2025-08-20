#!/usr/bin/env python3
""" """

import json
from datetime import datetime
import uuid
from server_env import env

class RouteRequestManager:
    in_progress_requests = []

    def __init__(self, data=None, route_id=None):
        self.request = data
        self.criterion = None
        
        self.route_id = route_id        
        self.session_id = None
        self.cache_id = None

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

    def create_initial_route(self):        
        initial_route = {
            "url": f"http://127.0.0.1:{env.port}/",
            "type": "initialRoute",
            "routing": [
                {
                    "request": self.request,
                    "response": {
                        "cacheId": f"{self.cache_id}",
                        "boundingBox": self.bounding_box,
                        "location": {
                            "limits": self.location_limits,
                            "urbanAreas": self.location_urban_areas,
                            "urbanCommunities": self.location_urban_communities,
                        },
                        "routes": [
                            self.route_for_gui()
                        ],
                    },
                }
            ],
        }
        return json.dumps(initial_route, indent=4, ensure_ascii=False)
    
    def create_custom_route(self):
        custom_route = {
            "type": "customRoute",
            "route": self.route_for_gui()
        }
        return json.dumps(custom_route, indent=4, ensure_ascii=False)
    
    def route_for_gui(self):
        route = {
            "routeId": self.route_id,
            "automatic": self.criterion != "ordered",
            "created": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "origin": self.origin,
            "waypoints": self.waypoints,
            "paths": self.paths,
            "estimatedDistance": self.estimated_distance,
            "estimatedTime": self.estimated_time,
        }
        return route

    @classmethod
    def process_request(cls, request_type, data):
        match request_type:
            case "shortest" | "circle" | "grid":
                route_id    = str(uuid.uuid4())

                new_request = cls(data, route_id)
                cls.in_progress_requests.append(new_request)
                return new_request, True

            case "ordered":
                route_id    = data["parameters"]["routeId"]

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