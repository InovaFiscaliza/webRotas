"""Process route endpoint"""

from fastapi import APIRouter, Query, Body
from fastapi.responses import JSONResponse

from webrotas.core.dependencies import (
    validate_request_structure,
    validate_request_type,
    validate_parameters,
)
from webrotas.services.route_service import process_route

router = APIRouter(tags=["routing"])


@router.post(
    "/process",
    summary="Process route request",
    description="Calculate optimal routes based on type and parameters",
    responses={
        200: {"description": "Route processed successfully"},
        400: {"description": "Invalid request or missing parameters"},
        500: {"description": "Server error during route processing"},
    }
)
async def process(
    session_id: str = Query(
        ...,
        alias="sessionId",
        description="Unique session identifier"
    ),
    request_data: dict = Body(...)
) -> JSONResponse:
    """
    Process a route request.
    
    The request must include:
    - `type`: Route type (shortest, circle, grid, or ordered)
    - `origin`: Starting point with lat, lng, description
    - `parameters`: Type-specific parameters
    - `criterion` (optional): Routing criterion (distance, duration, or ordered)
    - `avoidZones` (optional): Geographic zones to avoid
    """
    # Validate session_id
    if not session_id:
        from webrotas.core.exceptions import MissingSessionIdError
        raise MissingSessionIdError()
    
    # Validate request structure
    await validate_request_structure(request_data)
    
    # Validate request type
    request_type = request_data.get("type")
    await validate_request_type(request_type)
    
    # Validate parameters
    parameters = request_data.get("parameters")
    await validate_parameters(request_type, parameters)
    
    # Process the route
    response = await process_route(request_data, session_id)
    
    return JSONResponse(content=response)
