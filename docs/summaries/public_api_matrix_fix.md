# Public API Matrix Request Fix

## Problem

When requests were made without avoid zones, the matrix retrieval was failing because:
1. `_get_matrix_with_public_api_priority()` was supposed to use the public API
2. But it was calling `get_osrm_matrix()` which used `request_osrm()` 
3. `request_osrm()` internally calls `get_osrm_url()` which always returns the **local container URL**
4. Since the local container wasn't running, **all matrix requests failed**

The parallel public API fallback for avoid zones couldn't help because the non-avoid-zones path never reached it.

## Root Cause

**Code Flow (Before Fix):**
```
No avoid zones
  ↓
_get_matrix_with_public_api_priority()
  ↓
get_osrm_matrix() ← ❌ Uses request_osrm() → local URL!
  ↓
request_osrm()
  ↓
get_osrm_url() → http://localhost:5000 (not public API)
```

## Solution

Created a new `get_osrm_matrix_public_api()` function that explicitly uses the public OSRM API, and updated the fallback chain to use it.

**New Function (osrm.py lines 749-766):**
```python
async def get_osrm_matrix_public_api(coords):
    """Get matrix from public OSRM API (router.project-osrm.org)."""
    try:
        coord_str = ";\".join(f"{c['lng']},{c['lat']}" for c in coords)
        params = {
            "annotations": "distance,duration",
        }
        data = await request_osrm_public_api(  # ← Uses public API function
            request_type="table",
            coordinates=coord_str,
            params=params,
        )
        return data["distances"], data["durations"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_osrm_matrix_public_api: {e}")
        raise
```

**Updated Fallback (osrm.py line 571):**
```python
async def _get_matrix_with_public_api_priority(coords):
    try:
        return await get_osrm_matrix_public_api(coords)  # ← Now uses public API!
    except (httpx.HTTPError, ValueError, KeyError) as e:
        # Fallback to local container, then iterative builder, then geodesic
```

## Changes Made

- **File**: `src/webrotas/infrastructure/routing/osrm.py`
- **Line 749-766**: Added `get_osrm_matrix_public_api()` function
- **Line 571**: Updated `_get_matrix_with_public_api_priority()` to call `get_osrm_matrix_public_api()` instead of `get_osrm_matrix()`

## Corrected Flow (After Fix)

```
No avoid zones
  ↓
_get_matrix_with_public_api_priority()
  ↓
get_osrm_matrix_public_api() ← ✅ Uses request_osrm_public_api()
  ↓
request_osrm_public_api()
  ↓
"http://router.project-osrm.org" ← Public API!
  ↓
✅ Get distances and durations
```

## Result

- Requests without avoid zones now properly use the public OSRM API as a first attempt
- Matrix retrieval no longer fails when local container is unavailable
- Complete fallback chain: Public API → Local Container → Iterative Builder → Geodesic
