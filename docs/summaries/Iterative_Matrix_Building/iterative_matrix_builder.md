# Iterative Matrix Builder - Implementation Guide

## Overview

The `IterativeMatrixBuilder` is a fallback mechanism for constructing distance and duration matrices when the local OSRM container is unavailable. It iteratively requests batches from the public OSRM API while respecting rate limits and handling failures gracefully.

## Problem Solved

- **Public API Constraint**: The public OSRM API has a 100-waypoint limit per request
- **Large Coordinate Sets**: Routes with >100 points cannot be processed in a single request
- **Container Unavailability**: When the local container is down, large coordinate sets fail completely
- **Rate Limiting**: Naive requests would hit API rate limits or timeouts

## Architecture

### Algorithm

```
1. Split N coordinates into strategic batches
   - First pass: origin (0) → waypoints (1..N)  [chunks of 95]
   - Second pass: each waypoint as origin → remaining waypoints [chunks of 95]

2. For each batch:
   - Request matrix from public API
   - With exponential backoff on failure (1s → 2s → 4s)
   - Rate limit between requests (0.5s delay)

3. Merge responses into complete NxN matrix
   - Extract origin→waypoints distances/durations
   - Extract waypoint→waypoint sub-matrices

4. Fallback on failure:
   - Track failed pairs
   - Calculate geodesic distances for failures
   - Estimate durations using 40 km/h speed assumption
```

### Key Classes

#### `RequestBatch`
Represents a single API request batch:
- `origin_idx`: Index of the origin coordinate
- `waypoint_indices`: List of waypoint indices (max 95)
- `size`: Total coordinates (1 + len(waypoint_indices))
- `to_coord_string()`: Formats as OSRM URL parameter

#### `IterativeMatrixBuilder`
Main builder class:

```python
builder = IterativeMatrixBuilder(
    coords,
    batch_size=95,           # Waypoints per request
    max_retries=3,           # Retries per batch
    retry_delay=1.0,         # Base delay for exponential backoff (s)
    rate_limit_delay=0.5,    # Delay between requests (s)
)
distances, durations = builder.build()
```

### Configuration Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `batch_size` | 95 | Max waypoints per request (100 limit - 1 for safety) |
| `max_retries` | 3 | Retry attempts for failed requests |
| `retry_delay` | 1.0s | Initial backoff delay (doubles each retry) |
| `rate_limit_delay` | 0.5s | Delay between sequential requests |

## Integration Points

### In `api_routing.py`

The fallback chain:

```python
def controller(origin, waypoints, criterion="distance", avoid_zones=None):
    coords = [origin] + waypoints
    
    # 1. Try direct public API for small sets (<100)
    try:
        distances, durations = get_osrm_matrix(coords)
    except:
        # 2. Try local container
        try:
            distances, durations = get_osrm_matrix_from_local_container(coords)
        except:
            # 3. Try iterative builder
            try:
                distances, durations = get_osrm_matrix_iterative(coords)
            except:
                # 4. Fall back to geodesic
                distances, durations = get_geodesic_matrix(coords)
```

### When Iterative Builder is Used

1. **Public API fails** for large coordinate sets (>100 points)
2. **Local container unavailable** and coordinates exceed API limits
3. **Avoid zones present** but container is down

## Performance Characteristics

For N coordinates and batch size B:

- **Number of batches**: ~N²/(2B) for complete matrix
- **API requests**: Same as batch count
- **Total time**: `(batches - 1) × rate_limit_delay + API latency × batches`
- **Example**: 200 coords, batch 95:
  - Batches needed: ~421
  - Estimated time: 420 × 0.5s + API latency
  - With 1s API latency per batch: ~7 minutes

### Optimization Tips

1. **Reduce batch_size** if hitting rate limits
2. **Increase rate_limit_delay** if API is sensitive
3. **Decrease max_retries** if API is stable
4. **Pre-filter coordinates** to reduce matrix size

## Error Handling

### Failure Modes

| Scenario | Behavior | Result |
|----------|----------|--------|
| API timeout | Retry with backoff | Eventually geodesic fallback |
| Invalid response | Mark batch failed | Geodesic for that batch |
| All API calls fail | Use full geodesic | Slower but functional |
| Single batch fails | Retry then mark | Partial API + partial geodesic |

### Logging

All operations are logged with appropriate levels:

```
INFO:    Starting iterative matrix build for 250 coordinates with batch size 95
INFO:    Created 421 batches for API requests
DEBUG:   Processing batch 1/421 (origin 0, waypoints 95)
WARNING: Batch 42 failed after retries, will use geodesic fallback for failed pairs
INFO:    Applying geodesic fallback for 190 failed pairs
INFO:    Matrix build completed successfully
```

## Guarantees

1. **Valid matrices**: Diagonal is zero, all off-diagonals ≥ 0
2. **Approximate symmetry**: `distances[i][j] ≈ distances[j][i]` (via OSRM)
3. **Complete coverage**: All N² matrix elements populated
4. **Deterministic**: Same input → same output (given same API state)

## Testing

Test file: `tests/test_iterative_matrix_builder.py`

Test categories:

- **Batch creation**: Chunking logic, coverage, validity
- **Response merging**: Correct matrix population
- **Error handling**: Retries, fallback, invalid responses
- **Rate limiting**: Delay enforcement
- **Matrix integrity**: Symmetry, non-negative values, diagonal zeros
- **Edge cases**: Single coord, complete API failure

### Manual Testing

```python
webrotas.infrastructure.routing.matrix_builder import IterativeMatrixBuilder

# Create test coordinates
coords = [
    {"lat": -23.55 + i*0.01, "lng": -46.57 + i*0.01}
    for i in range(150)
]

# Build matrix
builder = IterativeMatrixBuilder(coords)
distances, durations = builder.build()

# Verify
assert len(distances) == 150
assert all(distances[i][i] == 0 for i in range(150))
print(f"Built {len(distances)}x{len(distances)} matrix successfully")
```

## Future Enhancements

1. **Caching**: Store successful API responses
2. **Parallel requests**: Make batch requests concurrently (respecting rate limits)
3. **Adaptive batch size**: Adjust based on API response times
4. **Matrix prediction**: Use distance heuristics to estimate missing values
5. **Fallback quality**: Use terrain/roads instead of pure geodesic
