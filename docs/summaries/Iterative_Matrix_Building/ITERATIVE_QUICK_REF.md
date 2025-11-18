# Iterative Matrix Builder - Quick Reference

## Problem & Solution

**Problem**: Public OSRM API limits requests to ~100 waypoints. When local container is unavailable and you have >100 coordinates, routing fails.

**Solution**: `IterativeMatrixBuilder` automatically chunks requests and builds the complete matrix in batches.

## Quick Start

### Basic Usage

```python
webrotas.infrastructure.routing.matrix_builder import IterativeMatrixBuilder

# Your coordinates (can have 100+ points)
coords = [
    {"lat": -23.55, "lng": -46.57},
    {"lat": -23.54, "lng": -46.58},
    # ... up to 1000+ coordinates
]

# Build matrix
builder = IterativeMatrixBuilder(coords)
distances, durations = builder.build()

# Use for routing
print(f"Distance 0->1: {distances[0][1]} meters")
print(f"Duration 0->1: {durations[0][1]} seconds")
```

### Custom Configuration

```python
builder = IterativeMatrixBuilder(
    coords,
    batch_size=80,           # Smaller if rate-limited
    max_retries=5,           # More if API unstable
    retry_delay=2.0,         # Longer backoff (1s->2s->4s)
    rate_limit_delay=1.0,    # Delay between requests
)
distances, durations = builder.build()
```

## How It Works

1. **Splits** N coordinates into batches of 95 waypoints (respects 100 API limit)
2. **Requests** matrix batches from public OSRM API sequentially
3. **Retries** failed requests with exponential backoff (1s → 2s → 4s)
4. **Rate limits** between requests (default 0.5s delay)
5. **Merges** responses into complete NxN distance/duration matrices
6. **Fallback**: Uses geodesic calculation for any failed pairs

## Performance

| Coords | Batches | Time | Notes |
|--------|---------|------|-------|
| 50 | 2 | <5s | Fast |
| 100 | 5 | ~10s | Typical |
| 200 | 25 | 1-2m | Common |
| 500 | 130 | 5-8m | Large |
| 1000 | 500 | 15-25m | Very large |

(Assumes 1s API latency per batch + 0.5s rate limit)

## Tuning

**If rate-limited:**
```python
builder = IterativeMatrixBuilder(coords, batch_size=50, rate_limit_delay=2.0)
```

**If API unstable:**
```python
builder = IterativeMatrixBuilder(coords, max_retries=5, retry_delay=2.0)
```

**If in a hurry:**
```python
builder = IterativeMatrixBuilder(coords, batch_size=95, max_retries=1, rate_limit_delay=0.2)
```

## Output

```python
distances  # NxN matrix [meters]
durations  # NxN matrix [seconds]

# Properties:
# distances[i][i] == 0  (same point)
# distances[i][j] >= 0  (never negative)
# distances[i][j] ≈ distances[j][i]  (symmetric)
```

## Automatic Integration

Used automatically in `api_routing.controller()` when:
1. Public API fails
2. Local container unavailable
3. Coordinates exceed API limits

Fallback chain:
```
Direct API → Local Container → Iterative Builder → Geodesic
```

## Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
builder = IterativeMatrixBuilder(coords)
builder.build()
```

Output shows batch progress, failures, and fallback statistics.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Many geodesic values | Longer `rate_limit_delay`, smaller `batch_size` |
| Too slow | Reduce `rate_limit_delay`, `max_retries`, or `batch_size` |
| Timeouts | Longer `retry_delay`, more `max_retries`, smaller `batch_size` |
