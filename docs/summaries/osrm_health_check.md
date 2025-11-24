# OSRM Container Health Check Implementation

## Overview
Added a dedicated health check endpoint for the OSRM container that performs a simple route request to verify the container is responding and operational.

## New Endpoint
**GET `/health/osrm`**

### Response Codes
- **200 OK**: OSRM container is healthy and responding
- **503 Service Unavailable**: OSRM container cannot be reached or returned an error
- **504 Gateway Timeout**: OSRM request exceeded the 5-second timeout

### Response Body (200 OK)
```json
{
  "status": "healthy",
  "osrm_url": "http://osrm:5000",
  "response_time_ms": 45.32,
  "message": "OSRM container is responding normally"
}
```

## Implementation Details

### Files Created
- **`src/webrotas/api/services/osrm_health.py`**: Service module with `check_osrm_health()` function
  - Sends a test route request to OSRM using predefined coordinates (Rio de Janeiro)
  - Measures response time in milliseconds
  - Validates JSON response structure and OSRM status code
  - Provides detailed error messages for connection, timeout, or service errors

### Files Modified
- **`src/webrotas/api/routes/health.py`**: Added new endpoint handler

## Usage Examples

### Using curl
```bash
curl http://127.0.0.1:5003/health/osrm
```

### Using the test script
```bash
bash tests/test_osrm_health.sh
```

## Error Handling
The health check handles multiple failure scenarios:
- **Connection Error**: OSRM container is not running or unreachable
- **Timeout**: OSRM service is slow to respond (>5 seconds)
- **Invalid Response**: OSRM returned non-JSON or error code
- **Service Error**: OSRM returned an error in the response

All errors are logged and return appropriate HTTP status codes with descriptive messages.

## Test Route
Uses a predefined test route between two points in Rio de Janeiro:
- Start: -43.105772903105354, -22.90510838815471
- End: -43.089637952126694, -22.917360518277434

This is a short, urban route that typically completes in milliseconds if OSRM is operational.

## Integration
- Uses existing `get_osrm_url()` from `server_hosts.py` for flexible configuration
- Works with both containerized (production) and development environments
- Logs all health check operations for monitoring and debugging
- Integrates with FastAPI OpenAPI documentation at `/docs` endpoint
