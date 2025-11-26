# Ordered Route Optimization

## Overview
Implemented performance optimization for "ordered" route requests by eliminating unnecessary distance matrix calculations. When waypoints are already in the desired order, the system now skips matrix computation and TSP solving, going directly to OSRM route calculation.

## Problem Statement
Previously, "ordered" requests used the same `calculate_optimal_route` function as other request types, which performed:
1. Distance/duration matrix calculation via OSRM table service
2. Matrix validation and repair
3. TSP (Traveling Salesman Problem) solving for waypoint optimization
4. OSRM route calculation

Since the "ordered" request type provides waypoints already in the desired order, the matrix calculation and TSP solving steps are redundant and waste computational resources.

## Solution

### New Function: `calculate_ordered_route`
**Location:** `src/webrotas/infrastructure/routing/osrm.py`

Optimized async function specifically for ordered waypoint processing:

```python
async def calculate_ordered_route(
    origin, waypoints, avoid_zones: List | None = None
)
```

**What it does:**
1. Filters waypoints inside exclusion zones (same as before)
2. Uses waypoints in provided order directly (no matrix needed)
3. Calls `get_osrm_route` with the sequential order
4. Formats and returns the route

**What it skips:**
- Matrix computation (no OSRM table requests)
- Matrix validation/repair
- TSP optimization

### Updated: `RouteProcessor.process_ordered`
**Location:** `src/webrotas/domain/routing/processor.py`

- Now calls `calculate_ordered_route` instead of `calculate_optimal_route`
- Updated docstring to clarify the optimization
- Same output format and compatibility with existing code

## Performance Impact

### Before Optimization
For an "ordered" request with N waypoints:
- 1× OSRM table request (N² waypoint pairs) ← **Eliminated**
- Matrix validation/repair processing ← **Eliminated**
- TSP solving (polynomial time) ← **Eliminated**
- 1× OSRM route request
- Elevation enrichment

### After Optimization
For an "ordered" request with N waypoints:
- 1× OSRM route request (only)
- Elevation enrichment

**Result:** Eliminates the most expensive operation (matrix calculation) for ordered requests.

## Backward Compatibility
- No API changes
- Request/response formats unchanged
- All filtering and elevation enrichment preserved
- Output identical to previous implementation
- Seamlessly integrated with existing flow

## Code Changes

### 1. New function in osrm.py
- Added `calculate_ordered_route()` function
- Mirrors `calculate_optimal_route` structure but skips matrix/TSP steps
- ~45 lines of code

### 2. Updated processor.py
- Changed import to include `calculate_ordered_route`
- Modified `process_ordered()` to call new function
- Updated docstring

## Testing Considerations
- "Ordered" requests should return identical results faster
- Matrix skipping doesn't affect route correctness
- Avoid zones filtering still applies
- Elevation enrichment still applied

## Future Optimization Opportunities
1. **Caching**: If same waypoint sets reused, cache route results
2. **Batch Processing**: Combine multiple ordered requests
3. **Streaming**: Return partial results during processing
4. **Parallel Segments**: Split route into segments for parallel processing

## Technical Details

### Why this optimization works
The TSP problem in `calculate_optimal_route` exists because we need to find the best order to visit waypoints. However, with "ordered" requests, the client has already solved this ordering problem and provides waypoints in the desired sequence. The OSRM route service will calculate the actual path and distances for any given waypoint order - the order just becomes a parameter.

### Zone Filtering Still Applied
The function still filters waypoints inside exclusion zones, which is important because:
- Filtered waypoints maintain the order (relative positions preserved)
- If waypoint N is inside a zone, waypoints N-1 and N+1 don't swap positions
- The sequential routing logic remains valid

### Elevation Enrichment Preserved
After route calculation, waypoints are enriched with elevation data using the same flow as before, ensuring consistency across all request types.
