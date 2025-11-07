"""Route processing service - extracted controller logic"""

from typing import Dict, Any
from webrotas.rotas import osrm_circle, osrm_grid, osrm_ordered, osrm_shortest
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

        # Route processing based on type
        match request_type:
            case "shortest":
                osrm_shortest(
                    current_request,
                    session_id,
                    origin,
                    parameters["waypoints"],
                    avoid_zones,
                    criterion,
                )
            case "circle":
                osrm_circle(
                    current_request,
                    session_id,
                    origin,
                    parameters["centerPoint"],
                    parameters["radius"],
                    parameters["totalWaypoints"],
                    avoid_zones,
                    criterion,
                )
            case "grid":
                osrm_grid(
                    current_request,
                    session_id,
                    origin,
                    parameters["city"],
                    parameters["state"],
                    parameters["scope"],
                    parameters["pointDistance"],
                    avoid_zones,
                    criterion,
                )
            case "ordered":
                osrm_ordered(
                    current_request,
                    session_id,
                    origin,
                    parameters["cacheId"],
                    parameters["boundingBox"],
                    parameters["waypoints"],
                    avoid_zones,
                    criterion,
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
