"""
Logs API endpoints for retrieving application and container logs.

Provides endpoints for:
- Fetching application logs with optional filtering
- Fetching container logs (OSRM)
- Retrieving combined logs from both sources
- Listing available log files
"""

from fastapi import APIRouter, Query
from typing import Optional

from webrotas.api.services.logs_service import (
    get_app_logs,
    get_log_files_info,
)
from webrotas.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get(
    "/app",
    summary="Get application logs",
    description="Retrieve recent application logs with optional filtering",
    responses={
        200: {"description": "Application logs retrieved successfully"},
        500: {"description": "Error retrieving logs"},
    },
)
async def get_app_logs_endpoint(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of log lines to return"
    ),
    log_level: Optional[str] = Query(
        None, description="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    ),
    module: Optional[str] = Query(None, description="Filter by module name pattern"),
):
    """
    Retrieve application logs.

    Query parameters:
    - limit: Maximum number of log lines (default: 100, max: 1000)
    - log_level: Filter by log level (optional)
    - module: Filter by module name pattern (optional)

    Returns:
        Dictionary containing filtered logs and metadata
    """
    try:
        result = get_app_logs(limit=limit, log_level=log_level, module_name=module)
        return result
    except Exception as e:
        logger.error(f"Error in get_app_logs_endpoint: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "logs": []}


# @router.get(
#     "/container",
#     summary="Get container logs",
#     description="Retrieve OSRM container logs",
#     responses={
#         200: {"description": "Container logs retrieved successfully"},
#         503: {"description": "Container not found or not running"},
#         500: {"description": "Error retrieving container logs"},
#     }
# )
# async def get_container_logs_endpoint(
#     container: str = Query("osrm", description="Container name"),
#     tail: int = Query(100, ge=1, le=1000, description="Number of most recent log lines to return"),
# ):
#     """
#     Retrieve OSRM container logs.

#     Query parameters:
#     - container: Container name (default: 'osrm')
#     - tail: Number of most recent lines (default: 100, max: 1000)

#     Returns:
#         Dictionary containing container logs and status
#     """
#     try:
#         result = get_container_logs(container_name=container, tail=tail)
#         return result
#     except Exception as e:
#         logger.error(f"Error in get_container_logs_endpoint: {e}", exc_info=True)
#         return {
#             "status": "error",
#             "message": str(e),
#             "container_name": container,
#             "logs": []
#         }


# @router.get(
#     "/",
#     summary="Get combined logs",
#     description="Retrieve both application and container logs in a single response",
#     responses={
#         200: {"description": "Combined logs retrieved successfully"},
#         500: {"description": "Error retrieving logs"},
#     }
# )
# async def get_combined_logs_endpoint(
#     app_limit: int = Query(50, ge=1, le=500, description="Maximum application log lines"),
#     container_tail: int = Query(50, ge=1, le=500, description="Maximum container log lines"),
#     container: str = Query("osrm", description="Container name"),
# ):
#     """
#     Retrieve combined application and container logs.

#     Query parameters:
#     - app_limit: Maximum application log lines (default: 50)
#     - container_tail: Maximum container log lines (default: 50)
#     - container: Container name (default: 'osrm')

#     Returns:
#         Dictionary containing both application and container logs
#     """
#     try:
#         result = get_combined_logs(
#             app_limit=app_limit,
#             container_tail=container_tail,
#             container_name=container
#         )
#         return result
#     except Exception as e:
#         logger.error(f"Error in get_combined_logs_endpoint: {e}", exc_info=True)
#         return {
#             "status": "error",
#             "message": str(e),
#             "app_logs": {"status": "error", "logs": []},
#             "container_logs": {"status": "error", "logs": []}
#         }


@router.get(
    "/files",
    summary="List log files",
    description="Get information about available log files",
    responses={
        200: {"description": "Log files listed successfully"},
        500: {"description": "Error retrieving log files"},
    },
)
async def get_log_files_endpoint():
    """
    Get information about available log files.

    Returns:
        Dictionary containing log files and their metadata
    """
    try:
        result = get_log_files_info()
        return result
    except Exception as e:
        logger.error(f"Error in get_log_files_endpoint: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "files": []}
