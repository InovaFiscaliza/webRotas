"""Route processing service - extracted controller logic"""

from typing import Dict, Any
from webrotas.rotas import RouteProcessor
from webrotas.route_request_manager import RouteRequestManager as rrm
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

        # Process or retrieve cached request
        current_request, new_request_flag = rrm.process_request(request_type, data)
        status = (
            "[webRotas] Created new request"
            if new_request_flag
            else "Using existing request"
        )
        print(
            f'{status} routeId="{current_request.route_id}" '
            f'(type="{request_type}", criterion="{criterion}", '
            f'sessionId="{session_id}")'
        )

        # Initialize RouteProcessor with common parameters
        processor = RouteProcessor(
            current_request,
            session_id,
            origin,
            avoid_zones,
            criterion,
        )

        # Route processing based on type
        match request_type:
            case "shortest":
                processor.process_shortest(parameters["waypoints"])
            case "circle":
                processor.process_circle(
                    parameters["centerPoint"],
                    parameters["radius"],
                    parameters["totalWaypoints"],
                )
            case "grid":
                processor.process_grid(
                    parameters["city"],
                    parameters["state"],
                    parameters["scope"],
                    parameters["pointDistance"],
                )
            case "ordered":
                processor.process_ordered(
                    parameters["cacheId"],
                    parameters["boundingBox"],
                    parameters["waypoints"],
                )

        # Generate response
        if request_type in {"shortest", "circle", "grid"}:
            response_json = current_request.create_initial_route()
        else:
            response_json = current_request.create_custom_route()

        # Convert Response object to dict if needed
        if isinstance(response_json, str):
            import json

            return json.loads(response_json)

        return response_json

    except ProcessingError:
        raise
    except Exception as e:
        raise ProcessingError(str(e))
