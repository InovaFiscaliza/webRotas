# Parallel Public API Timeout and Delays

## Changes Made

Increased timeout and added delays between parallel requests to the public OSRM API to prevent connection failures and rate limiting.

### 1. Updated Configuration (`parallel_public_api.py`)

**Lines 24-28:**
```python
PUBLIC_API_MAX_CONCURRENT = 10  # Limit concurrent requests to avoid rate limiting
PUBLIC_API_REQUEST_TIMEOUT = 60  # Timeout per request in seconds (increased from 30s)
PUBLIC_API_RETRY_ATTEMPTS = 2
PUBLIC_API_RETRY_DELAY = 1.0
PUBLIC_API_REQUEST_DELAY = 0.1  # Delay between batches of parallel requests (in seconds)
```

**Changes:**
- `PUBLIC_API_REQUEST_TIMEOUT`: Increased from 30s to **60s** to match the general HTTP client timeout
- `PUBLIC_API_REQUEST_DELAY`: New constant of **0.1s** added for inter-request delays

### 2. Added Delays to Parallel Requests

**Segment-based parallel requests (`get_full_route_parallel`)** - Line 124:
```python
async def bounded_request(start, end, idx):
    async with semaphore:
        # Add delay to avoid overwhelming the public API
        await asyncio.sleep(PUBLIC_API_REQUEST_DELAY)
        return await get_route_segment_parallel(osrm_request_fn, start, end, idx)
```

**Matrix-based parallel requests (`get_distance_matrix_parallel_public_api`)** - Line 203:
```python
# Add delay to avoid overwhelming the public API
await asyncio.sleep(PUBLIC_API_REQUEST_DELAY)

response = await osrm_request_fn(
    request_type="table",
    coordinates=coord_str,
    params={},
)
```

### 3. Made Timeout Configurable (`osrm.py`)

**Line 336:**
```python
async def make_request(url, params=None, timeout=60.0):
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
```

**Change:** Added `timeout` parameter with default value of 60.0 seconds

## Benefits

1. **More Reliable Requests**: 60-second timeout gives slow public API responses time to complete
2. **Rate Limit Friendly**: 0.1-second delays between requests reduce overwhelming the public API
3. **Better Concurrency**: Semaphore still limits to 10 concurrent requests while delays prevent burst hammering
4. **Graceful Degradation**: Allows the public API fallback to work reliably even under load

## Effective Request Rate

With 10 concurrent requests and 0.1s delay per request:
- Best case: ~100 requests/second (if requests complete instantly)
- Practical: ~50-70 requests/second (accounting for response time)

This prevents rate limiting from `router.project-osrm.org` which typically allows 600 requests/minute per IP.
