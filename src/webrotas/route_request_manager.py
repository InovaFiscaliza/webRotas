#!/usr/bin/env python3
""" """

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid
from typing import Any
from webrotas.server_env import env
from webrotas.config.server_hosts import get_webrotas_url


@dataclass
class RouteRequestManager:
    in_progress_requests: list = field(default_factory=list, init=False, repr=False)

    request: Any = None
    route_id: str | None = None

    criterion: str | None = None
    session_id: str | None = None
    cache_id: str | None = None

    routing_area: Any = None
    bounding_box: Any = None
    avoid_zones: Any = None

    location_limits: Any = None
    location_urban_areas: Any = None
    location_urban_communities: Any = None

    origin: Any = None
    waypoints: Any = None
    paths: Any = None

    estimated_distance: Any = None
    estimated_time: Any = None

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def create_initial_route(self):
        initial_route = {
            "url": f"{get_webrotas_url(env.port)}/",
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
                        "routes": [self.route_for_gui()],
                    },
                }
            ],
        }
        return json.dumps(initial_route, indent=4, ensure_ascii=False)

    def create_custom_route(self):
        custom_route = {"type": "customRoute", "route": self.route_for_gui()}
        return json.dumps(custom_route, indent=4, ensure_ascii=False)

    def route_for_gui(self):
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

    @classmethod
    def process_request(cls, request_type, data):
        match request_type:
            case "shortest" | "circle" | "grid":
                route_id = str(uuid.uuid4())

                new_request = cls(request=data, route_id=route_id)
                new_request.in_progress_requests.append(new_request)
                return new_request, True

            case "ordered":
                route_id = data["parameters"]["routeId"]

                old_request = cls.find_by_route_id(route_id)
                if old_request:
                    return old_request, False

                new_request = cls(request=data, route_id=route_id)
                new_request.in_progress_requests.append(new_request)
                return new_request, True

            case _:
                raise ValueError(f"Unknown request type: {request_type}")

    @classmethod
    def find_by_route_id(cls, route_id):
        # Access the class variable from an instance
        instance = cls()
        return next(
            (req for req in instance.in_progress_requests if req.route_id == route_id),
            None,
        )
