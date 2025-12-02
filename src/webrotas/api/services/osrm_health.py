"""OSRM container health check service"""

import time
import httpx
from typing import Dict, Any
from fastapi import HTTPException

from webrotas.config.server_hosts import get_osrm_url
from webrotas.config.logging_config import get_logger


logger = get_logger(__name__)

# Test route coordinates: simple route in Rio de Janeiro, Brazil
TEST_ROUTE_PATH = "/route/v1/driving/-43.105772903105354,-22.90510838815471;-43.089637952126694,-22.917360518277434?overview=full&geometries=polyline&steps=true"
TIMEOUT = 5


async def check_osrm_health() -> Dict[str, Any]:
    """
    Perform a health check on the OSRM container by executing a simple route request.
    
    Returns:
        Dictionary with health status containing:
        - status: 'healthy' or 'unhealthy'
        - osrm_url: URL of OSRM server that was tested
        - response_time_ms: Time taken for OSRM to respond
        - message: Descriptive status message
        
    Raises:
        HTTPException: If OSRM is not responding or returns an error
    """
    osrm_url = get_osrm_url()
    request_url = f"{osrm_url}{TEST_ROUTE_PATH}"
    
    try:
        logger.info(f"Starting OSRM health check: {request_url}")
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(request_url)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        if response.status_code != 200:
            logger.error(f"OSRM returned status {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=503,
                detail=f"OSRM service returned status {response.status_code}"
            )
        
        # Validate response contains expected routing data
        try:
            data = response.json()
            if data.get("code") != "Ok":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"OSRM returned error code: {data.get('code')} - {error_msg}")
                raise HTTPException(
                    status_code=503,
                    detail=f"OSRM service error: {error_msg}"
                )
        except ValueError as e:
            logger.error(f"OSRM response is not valid JSON: {e}")
            raise HTTPException(
                status_code=503,
                detail="OSRM service returned invalid response"
            )
        
        logger.info(f"OSRM health check successful ({response_time_ms:.2f}ms)")
        
        return {
            "status": "healthy",
            "osrm_url": osrm_url,
            "response_time_ms": round(response_time_ms, 2),
            "message": "OSRM container is responding normally"
        }
        
    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to OSRM at {osrm_url}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to OSRM service at {osrm_url}"
        )
    except httpx.TimeoutException as e:
        logger.error(f"OSRM request timed out after {TIMEOUT}s: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"OSRM service did not respond within {TIMEOUT} seconds"
        )
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during OSRM health check: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Unexpected error during OSRM health check"
        )
