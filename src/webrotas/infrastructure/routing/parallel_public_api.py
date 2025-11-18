"""
Parallel Public API routing for avoid zones.

When avoid zones are present but the local OSRM container is unavailable,
this module provides parallel async requests to the Public OSRM API using
2-point coordinates (which support alternatives).

Strategy:
1. Decompose multi-point route into 2-point segments
2. Request each segment's alternatives in parallel from Public API
3. Combine segments into complete routes
4. Select best route based on avoid zone penalties
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Any, Optional

from webrotas.config.logging_config import get_logger

logger = get_logger(__name__)

# Configuration for parallel requests
PUBLIC_API_MAX_CONCURRENT = 10  # Limit concurrent requests to avoid rate limiting
PUBLIC_API_REQUEST_TIMEOUT = 60  # Timeout per request in seconds (increased from 30s)
PUBLIC_API_RETRY_ATTEMPTS = 2
PUBLIC_API_RETRY_DELAY = 1.0
PUBLIC_API_REQUEST_DELAY = 0.1  # Delay between batches of parallel requests (in seconds)


async def request_osrm_parallel(request_type: str, coordinates: str, params: dict = None):
    """
    Make an async request to OSRM.
    
    This is a placeholder that would be implemented in the calling module.
    The actual OSRM request function is passed as a callback.
    """
    pass


async def get_route_segment_parallel(
    osrm_request_fn,
    start_coord: Dict[str, float],
    end_coord: Dict[str, float],
    segment_index: int,
) -> Optional[Dict[str, Any]]:
    """
    Request alternatives for a single 2-point segment from Public API.
    
    Args:
        osrm_request_fn: Async function to make OSRM requests
        start_coord: Starting point {lat, lng}
        end_coord: Ending point {lat, lng}
        segment_index: Index of this segment
    
    Returns:
        Dict with best route or None if failed
    """
    try:
        coord_str = f"{start_coord['lng']},{start_coord['lat']};{end_coord['lng']},{end_coord['lat']}"
        
        params = {
            "alternatives": 3,
            "overview": "full",
            "geometries": "geojson",
        }
        
        logger.debug(f"Requesting alternatives for segment {segment_index}: {coord_str}")
        
        response = await osrm_request_fn(
            request_type="route",
            coordinates=coord_str,
            params=params,
        )
        
        if response and response.get("routes"):
            best_route = response["routes"][0]
            return {
                "segment_index": segment_index,
                "geometry": best_route.get("geometry", {}).get("coordinates", []),
                "distance": best_route.get("distance", 0),
                "duration": best_route.get("duration", 0),
                "alternatives": len(response.get("routes", [])),
            }
        
        logger.warning(f"No routes returned for segment {segment_index}")
        return None
        
    except Exception as e:
        logger.warning(f"Error requesting segment {segment_index}: {e}")
        return None


async def get_full_route_parallel(
    osrm_request_fn,
    coords: List[Dict[str, float]],
) -> Tuple[List, float, float]:
    """
    Get full route using parallel 2-point segment requests.
    
    Args:
        osrm_request_fn: Async function to make OSRM requests
        coords: List of coordinates (origin + waypoints)
    
    Returns:
        Tuple of (path_coordinates, total_distance, total_duration)
    """
    if len(coords) < 2:
        raise ValueError("At least 2 coordinates required")
    
    # Create segments (2-point pairs)
    segments = []
    for i in range(len(coords) - 1):
        segments.append((coords[i], coords[i + 1], i))
    
    logger.info(f"Requesting {len(segments)} segments in parallel")
    
    # Request all segments in parallel with concurrency limit
    semaphore = asyncio.Semaphore(PUBLIC_API_MAX_CONCURRENT)
    
    async def bounded_request(start, end, idx):
        async with semaphore:
            # Add delay to avoid overwhelming the public API
            await asyncio.sleep(PUBLIC_API_REQUEST_DELAY)
            return await get_route_segment_parallel(osrm_request_fn, start, end, idx)
    
    tasks = [bounded_request(start, end, idx) for start, end, idx in segments]
    results = await asyncio.gather(*tasks)
    
    # Check if all segments succeeded
    if any(r is None for r in results):
        failed_count = sum(1 for r in results if r is None)
        raise ValueError(f"Failed to get route for {failed_count} segments")
    
    # Combine segment geometries into full path
    full_path = []
    total_distance = 0
    total_duration = 0
    
    for result in results:
        # Skip the first point of each segment except the first segment (to avoid duplicates)
        geometry = result["geometry"]
        if result["segment_index"] > 0 and geometry:
            geometry = geometry[1:]  # Skip first point
        full_path.extend(geometry)
        total_distance += result["distance"]
        total_duration += result["duration"]
    
    logger.info(
        f"✅ Got full route via parallel Public API: "
        f"{len(full_path)} points, {total_distance/1000:.1f}km, {total_duration/60:.1f}min"
    )
    
    return full_path, total_distance, total_duration


async def get_distance_matrix_parallel_public_api(
    osrm_request_fn,
    coords: List[Dict[str, float]],
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Build distance/duration matrices using parallel 2-point requests.
    
    This is computationally intensive for large coordinate sets, but provides
    a fallback when the local OSRM container is unavailable.
    
    Args:
        osrm_request_fn: Async function to make OSRM requests
        coords: List of coordinates
    
    Returns:
        Tuple of (distance_matrix, duration_matrix)
    """
    n = len(coords)
    
    if n > 100:
        logger.warning(
            f"⚠️ Building matrix for {n} coordinates using parallel Public API. "
            f"This will make {n*(n-1)//2} requests and may hit rate limits."
        )
    
    # Create all 2-point pairs
    requests = []
    for i in range(n):
        for j in range(i + 1, n):
            requests.append((i, j, coords[i], coords[j]))
    
    logger.info(f"Requesting distance/duration for {len(requests)} coordinate pairs")
    
    # Initialize matrices
    distances = [[0.0] * n for _ in range(n)]
    durations = [[0.0] * n for _ in range(n)]
    
    # Request all pairs in parallel with concurrency limit
    semaphore = asyncio.Semaphore(PUBLIC_API_MAX_CONCURRENT)
    
    async def bounded_pair_request(i, j, start, end):
        async with semaphore:
            try:
                coord_str = f"{start['lng']},{start['lat']};{end['lng']},{end['lat']}"
                
                # Add delay to avoid overwhelming the public API
                await asyncio.sleep(PUBLIC_API_REQUEST_DELAY)
                
                response = await osrm_request_fn(
                    request_type="table",
                    coordinates=coord_str,
                    params={"annotations": "distance,duration"},
                )
                
                if response and response.get("distances") and response.get("durations"):
                    dist = response["distances"][0][1]
                    dur = response["durations"][0][1]
                    
                    # Store both directions
                    distances[i][j] = dist
                    distances[j][i] = dist
                    durations[i][j] = dur
                    durations[j][i] = dur
                    
                    return (i, j, dist, dur)
                else:
                    logger.warning(f"Invalid response for pair ({i}, {j})")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error requesting pair ({i}, {j}): {e}")
                return None
    
    tasks = [
        bounded_pair_request(i, j, start, end)
        for i, j, start, end in requests
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Check for failures
    failed_count = sum(1 for r in results if r is None)
    if failed_count > 0:
        logger.warning(f"⚠️ {failed_count}/{len(requests)} requests failed")
    
    logger.info(f"✅ Built {n}x{n} matrices via parallel Public API")
    
    return distances, durations
