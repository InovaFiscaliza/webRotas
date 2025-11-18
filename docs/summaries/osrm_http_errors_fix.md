# OSRM HTTP Connection Errors Fix

## Problem

When the local OSRM container was unavailable and avoid zones were present, the parallel public API fallback would fail with connection errors:

```
[ERROR] webrotas.infrastructure.routing.osrm - OSRM HTTP error: All connection attempts failed
```

All 171+ coordinate pair requests would fail with `502: OSRM routing request failed: All connection attempts failed`.

## Root Cause

The `parallel_public_api.get_distance_matrix_parallel_public_api()` function was being passed the `request_osrm` callback function. However, `request_osrm` internally uses `get_osrm_url()` which always returns the local container URL (`http://localhost:5000`):

```python
async def request_osrm(request_type: str, coordinates: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{get_osrm_url()}/{request_type}/v1/driving/{coordinates}"  # Always local URL
```

When the local container wasn't running, this caused connection failures. The parallel API logic was attempting to use the **public** API endpoint but was still pointing to the **local** container URL.

## Solution

Created a new `request_osrm_public_api()` function that explicitly uses the public OSRM endpoint:

```python
async def request_osrm_public_api(
    request_type: str,
    coordinates: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """Request route from public OSRM API (router.project-osrm.org)."""
    try:
        assert request_type in {"route", "table"}, "Invalid request type"
        url = f"http://router.project-osrm.org/{request_type}/v1/driving/{coordinates}"  # Public URL
        data = await make_request(url, params=params)
        return data
    except httpx.HTTPError as e:
        logger.error(f"OSRM HTTP error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"OSRM routing request failed: {str(e)}",
        )
```

Updated the parallel API callback from:
```python
return await get_distance_matrix_parallel_public_api(request_osrm, coords)
```

To:
```python
return await get_distance_matrix_parallel_public_api(request_osrm_public_api, coords)
```

## Changes Made

- **File**: `src/webrotas/infrastructure/routing/osrm.py`
- **Line 383-421**: Added `request_osrm_public_api()` function
- **Line 513**: Updated parallel API call to use `request_osrm_public_api` instead of `request_osrm`

## Fallback Chain (With Fix)

When avoid zones are present and local OSRM container is unavailable:

1. ✗ Try local OSRM container
2. ✅ **Parallel public API requests** (now works correctly)
3. Iterative matrix builder (if no avoid zones)
4. Geodesic calculation (last resort)

## Testing

The fix ensures that when the local OSRM container is unavailable:
- Parallel public API requests now connect to `router.project-osrm.org` instead of `localhost:5000`
- Matrix building succeeds with proper distance/duration values from the public API
- Avoid zone processing continues with the fallback data
