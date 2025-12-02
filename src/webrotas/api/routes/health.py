"""Health check endpoint"""

from fastapi import APIRouter, Query

from webrotas.api.services.osrm_health import check_osrm_health


router = APIRouter(tags=["health"])


@router.get(
    "/ok",
    summary="Health check",
    description="Verify server is running and responsive",
    responses={
        200: {"description": "Server is healthy"},
        400: {"description": "Missing sessionId"},
    }
)
async def health_check(session_id: str = Query(..., alias="sessionId", description="Unique session identifier")):
    """
    Health check endpoint.
    
    Returns JSON status if the server is running properly.
    """
    # Validate session_id
    if not session_id:
        from webrotas.core.exceptions import MissingSessionIdError
        raise MissingSessionIdError()
    return {"status": "healthy"}


@router.get(
    "/health/osrm",
    summary="OSRM container health check",
    description="Verify OSRM container is running and responding to route requests",
    responses={
        200: {"description": "OSRM container is healthy"},
        503: {"description": "OSRM container is unavailable or not responding"},
        504: {"description": "OSRM request timed out"},
    }
)
async def osrm_health_check():
    """
    OSRM container health check endpoint.
    
    Performs a simple route request to verify the OSRM container is operational.
    Returns timing information and service status.
    """
    return await check_osrm_health()
