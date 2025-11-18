# Avoid Zones Implementation Summary

## Problem Statement

The webRotas routing system needed to support avoid zones - geographic areas that routes should minimize passing through. The challenge was that OSRM (Open Source Routing Machine) has a fundamental limitation: **alternatives only compute for 2-coordinate (origin-destination) requests**, not for multi-waypoint routes with 3+ coordinates.

## Solution Architecture

### 1. **Segment-Based Alternatives** (`domain/routing/alternatives.py`)

For multi-waypoint requests with avoid zones:

- **Decompose** the route into 2-coordinate segments (A→B, B→C, C→D)
- **Request alternatives** for each segment in parallel using OSRM
- **Combine** segment alternatives into complete routes
- **Score** each complete route based on zone intersection penalties

**Key benefit:** Enables alternatives for multi-waypoint routes, which OSRM doesn't natively support.

```
Original: Osasco → Ibirapuera → Anatel (3 waypoints, no alternatives in OSRM)
           ↓
Segments: [Osasco→Ibirapuera], [Ibirapuera→Anatel] (2 coordinates each)
           ↓
Get alternatives for each segment (OSRM supports this)
           ↓
Combine: Route1, Route2, Route3 (3 complete alternatives)
```

### 2. **Zone-Aware Routing** (`domain/routing/zone_aware.py`)

When all segment-based alternatives still cross avoid zones:

- **Generate boundary waypoints** around zone perimeter at progressive offsets (1.5km, 3km, 5km, 7.5km, 10km)
- **Try single and paired waypoint routes** through boundary points
- **Select the best alternative** with lowest zone penalty score (10%+ improvement required)

**Key benefit:** Attempts to find routes that minimize zone overlap through dynamic waypoint insertion.

### 3. **httpx Request Fix** (`infrastructure/routing/osrm.py`)

Fixed async HTTP requests to properly handle URL parameters:

```python
# BEFORE (incorrect):
response = await client.get(url, params=params)  # May cause duplicate parameters

# AFTER (correct):
request_url = httpx.URL(url, params=params)      # Properly merges parameters
response = await client.get(request_url)
```

**Why it matters:** The OSRM API base URLs already contain query parameters. Using `httpx.URL()` ensures proper parameter handling instead of accidentally duplicating query strings.

## Integration Points

### In `get_osrm_route()` function:

1. **Detect** multi-waypoint requests (3+) with avoid zones
2. **Use segment-based alternatives** as primary approach
3. **Fall back to zone-aware routing** if all alternatives cross zones
4. **Prioritize** routes by penalty score (less zone overlap = better)
5. **Return** routes with detailed penalty metadata

### Response Format:

Each route includes penalty information:

```json
{
  "geometry": {...},
  "distance": 27950,
  "duration": 2212,
  "penalties": {
    "zone_intersections": 1,
    "penalty_score": 0.0316
  }
}
```

## Limitations & Constraints

### Fundamental Limitation

When a large avoid zone geometrically blocks the direct path between mandatory waypoints, **OSRM will still route through it** because that's the optimal path. This is unavoidable without OSRM preprocessing-based avoid profiles.

### What Works Well

- Scenarios where **some alternatives avoid zones better than others**
- Routes with **multiple zones** that don't completely block paths
- Providing **visibility** into zone intersection metrics for informed routing

### OSRM Constraints

- **Maximum 3 alternatives** per request (OSRM limitation)
- **2-coordinate requests only** for alternatives
- Cannot truly "force" avoidance without preprocessing

## Technical Details

### Files Created/Modified

**New modules:**
- `src/webrotas/domain/routing/alternatives.py` - Segment-based alternatives
- `src/webrotas/domain/routing/zone_aware.py` - Zone-aware routing with waypoint insertion

**Modified modules:**
- `src/webrotas/infrastructure/routing/osrm.py` - Integration & httpx fix

### Key Functions

**Segment-based:**
- `SegmentAlternativesBuilder.decompose_into_segments()` - Break route into 2-coord pairs
- `SegmentAlternativesBuilder.request_segment_alternatives()` - Request OSRM alternatives
- `SegmentAlternativesBuilder.generate_complete_routes()` - Combine segments into routes

**Zone-aware:**
- `generate_boundary_waypoints()` - Create waypoints around zone boundaries
- `try_route_with_intermediate_waypoints()` - Route through waypoint pairs
- `find_route_around_zones()` - Main zone-aware routing orchestration

**Infrastructure:**
- `make_request()` - Fixed httpx async request handling
- `request_osrm()` - OSRM API wrapper with proper error handling
- `request_osrm_public_api()` - Public API fallback

## Testing

Two test scripts verify the implementation:

1. **`test_integration.py`** - Tests segment-based alternatives
2. **`test_zone_aware.py`** - Tests zone-aware routing with Osasco scenario
3. **`test_httpx_fix.py`** - Verifies httpx URL parameter handling

## Performance Considerations

- **Parallel segment requests** using `asyncio.gather()` for speed
- **Progressive offset distances** to minimize unnecessary attempts
- **Early exit** if single-waypoint route improvement is found
- **Timeout handling** for HTTP requests (60 second default)

## Future Improvements

1. **Preprocessing-based profiles** - If OSRM data can be rebuilt with avoid profiles
2. **Smarter boundary waypoint generation** - Consider actual street network around zones
3. **Caching** - Store computed alternatives for repeated requests
4. **Multi-zone optimization** - Better handling when multiple zones block the route
5. **Weighted zones** - Allow zones with different avoidance priorities
