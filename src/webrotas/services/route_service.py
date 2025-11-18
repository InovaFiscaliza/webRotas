"""Route processing service - extracted controller logic"""

import json
import uuid
from typing import Dict, Any
from webrotas.domain.routing.processor import RouteProcessor
from webrotas.core.exceptions import ProcessingError


async def process_route(data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """
    Process a route request and return the result as a JSON-serializable dict.

    Args:
        data: Request data containing type, origin, parameters, etc.
        session_id: Unique session identifier

    Returns:
        JSON-serializable route response

    Raises:
        ProcessingError: If route processing fails
    """
    try:
        request_type = data["type"]
        origin = data["origin"]
        parameters = data["parameters"]
        avoid_zones = data.get("avoidZones", [])
        criterion = data.get("criterion", "distance")

        # Generate route ID based on request type
        if request_type in {"shortest", "circle", "grid"}:
            route_id = str(uuid.uuid4())
            is_new_request = True
        elif request_type == "ordered":
            route_id = parameters["routeId"]
            # Note: cached request lookup not implemented - async eliminates need
            is_new_request = True
        else:
            raise ValueError(f"Unknown request type: {request_type}")

        status = (
            "[webRotas] Created new request"
            if is_new_request
            else "Using existing request"
        )
        print(
            f'{status} routeId="{route_id}" '
            f'(type="{request_type}", criterion="{criterion}", '
            f'sessionId="{session_id}")'
        )

        # Initialize RouteProcessor with common parameters
        processor = RouteProcessor(
            session_id=session_id,
            origin=origin,
            avoid_zones=avoid_zones,
            criterion=criterion,
            request_data=data,
            route_id=route_id,
        )

        # Route processing based on type
        match request_type:
            case "shortest":
                await processor.process_shortest(parameters["waypoints"])
            case "circle":
                await processor.process_circle(
                    parameters["centerPoint"],
                    parameters["radius"],
                    parameters["totalWaypoints"],
                )
            case "grid":
                await processor.process_grid(
                    parameters["city"],
                    parameters["state"],
                    parameters["scope"],
                    parameters["pointDistance"],
                )
            case "ordered":
                await processor.process_ordered(
                    parameters["cacheId"],
                    parameters["boundingBox"],
                    parameters["waypoints"],
                )

        # Generate response
        if request_type in {"shortest", "circle", "grid"}:
            response_json = processor.create_initial_route()
        else:
            response_json = processor.create_custom_route()

        # Convert Response object to dict if needed
        if isinstance(response_json, str):
            return json.loads(response_json)

        return response_json

    except ProcessingError:
        raise
    except Exception as e:
        raise ProcessingError(str(e))
