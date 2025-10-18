"""Health check endpoint"""

from fastapi import APIRouter, Query

from core.dependencies import validate_session_id

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
    
    Returns 'ok' if the server is running properly.
    """
    # Validate session_id
    if not session_id:
        from core.exceptions import MissingSessionIdError
        raise MissingSessionIdError()
    return "ok"
