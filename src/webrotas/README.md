# FastAPI webRotas - Quick Start Guide

## Overview
webRotas has been migrated from Flask to FastAPI. The application maintains 100% backward compatibility while gaining improved performance, automatic API documentation, and better code organization.

## Installation & Setup

### Install Dependencies
```bash
cd /home/ronaldo/Work/webRotas
uv sync
```

## Running the Server

### Option 1: Using main.py (Recommended)
```bash
cd src/
uv run python main.py --port 5002
```

### Option 2: Using Uvicorn directly (Development)
```bash
cd src/
uv run uvicorn main:app --reload --port 5002
```

### Option 3: Using Uvicorn (Production)
```bash
cd src/
uv run uvicorn main:app --host 0.0.0.0 --port 5002 --workers 4
```

## API Endpoints

### 1. Health Check
**Endpoint**: `GET /ok`

```bash
curl "http://127.0.0.1:5002/ok?sessionId=test123"
```

**Response**: `"ok"`

**Status**: 200 OK or 422 if sessionId is missing

---

### 2. Process Route
**Endpoint**: `POST /process`

```bash
curl -X POST "http://127.0.0.1:5002/process?sessionId=test123" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "shortest",
    "origin": {
      "lat": -23.5505,
      "lng": -46.6333,
      "description": "São Paulo"
    },
    "parameters": {
      "waypoints": [
        {"lat": -23.55, "lng": -46.63},
        {"lat": -23.56, "lng": -46.64}
      ]
    },
    "criterion": "distance"
  }'
```

**Request Fields**:
- `type` (required): `"shortest"`, `"circle"`, `"grid"`, or `"ordered"`
- `origin` (required): Object with `lat`, `lng`, `description`, and optional `elevation`
- `parameters` (required): Type-specific parameters
- `criterion` (optional): `"distance"`, `"duration"`, or `"ordered"` (default: `"distance"`)
- `avoidZones` (optional): List of zones to avoid

---

## Using the CLI Client

The CLI client remains unchanged and works with the FastAPI server:

```bash
# Test with existing payload
uv run src/ucli/webrota_client.py tests/request_shortest*.json

# Or with a specific request
uv run src/ucli/webrota_client.py tests/request_circle_20_points.json
```

---

## API Documentation (Auto-Generated)

### Swagger UI
Open in browser: **http://localhost:5002/docs**

This provides an interactive API explorer where you can:
- See all available endpoints
- View request/response schemas
- Test endpoints directly from the browser
- View example payloads

### ReDoc
Open in browser: **http://localhost:5002/redoc**

Alternative documentation format with a cleaner, more readable layout.

### OpenAPI Schema (JSON)
**URL**: http://localhost:5002/openapi.json

Raw OpenAPI 3.0 schema for use with API clients and tools.

---

## Code Organization

```
src//
├── main.py                          # FastAPI app entry point
├── config/constants.py              # Validation rules
├── core/
│   ├── exceptions.py               # Custom error handling
│   └── dependencies.py             # Validation utilities
├── api/
│   ├── routes/
│   │   ├── health.py              # /ok endpoint
│   │   └── process.py             # /process endpoint
│   └── models/requests.py          # Pydantic data models
├── services/route_service.py        # Business logic
└── [existing files unchanged]
```

---

## Request Validation

All validation is automatic via Pydantic models:

1. **Session ID**: Must be provided as query parameter `?sessionId=<value>`
2. **Request Type**: Must be one of: `shortest`, `circle`, `grid`, `ordered`
3. **Origin**: Must have `lat` (float), `lng` (float), `description` (string)
4. **Parameters**: Type-specific and validated accordingly
5. **Criterion**: Must be one of: `distance`, `duration`, `ordered`

---

## Error Responses

### Missing Session ID
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "sessionId"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```
Status: 422

### Invalid Request Type
```json
{
  "detail": "Invalid or missing request type: 'invalid_type'"
}
```
Status: 400

### Missing Required Parameters
```json
{
  "detail": "Missing required parameters for type 'circle': ['radius', 'totalWaypoints']"
}
```
Status: 400

### Processing Error
```json
{
  "detail": "Processing error: <error message>"
}
```
Status: 500

---

## Performance Tips

1. **Use production uvicorn** for better performance:
   ```bash
   uv run uvicorn main:app --port 5002 --workers 4
   ```

2. **Enable compression**: Automatically enabled for responses > 1000 bytes

3. **Use connection pooling**: For external API calls (built-in with requests library)

---

## Troubleshooting

### Server won't start
- Check if port is already in use: `lsof -i :5002`
- Ensure you're running from `src/` directory
- Check for Python import errors in console output

### Endpoint returns 422 error
- Verify query parameters use correct names (e.g., `sessionId` not `session_id`)
- Check JSON request body is valid

### Static files not loading
- Verify `static/` directory exists in `src//`
- Check file permissions on static directory

### Slower than expected
- Run with `--workers 4` for production
- Check system resources (CPU, memory)
- Compare with original Flask version using load testing

---

## Comparison: Flask vs FastAPI

| Feature            | Flask     | FastAPI                   |
| ------------------ | --------- | ------------------------- |
| Auto Documentation | ❌ No      | ✅ Yes (`/docs`, `/redoc`) |
| Type Validation    | ❌ Manual  | ✅ Automatic (Pydantic)    |
| Async Support      | ⚠️ Limited | ✅ Full                    |
| Error Messages     | ⚠️ Generic | ✅ Detailed                |
| Performance        | Good      | ✅ Excellent               |
| Development        | ✅ Simple  | ✅ More structured         |
| CORS/Compression   | Manual    | ✅ Built-in                |

---

## Migration Differences

### What Changed
- Framework: Flask → FastAPI
- ASGI Server: Werkzeug → Uvicorn
- Request validation: Manual → Pydantic models
- Error handling: Flask exceptions → FastAPI HTTPException

### What Didn't Change
- API endpoints (`/ok`, `/process`)
- Request/response format
- Business logic (web_rotas, route calculations)
- File structure (external services, cache, etc.)
- Configuration (ports, logging)

---

## Next Steps

1. **Test with real data**: Use your test request files
2. **Monitor performance**: Compare with original Flask version
3. **Validate results**: Ensure route calculations are identical
4. **Deploy gradually**: Test in staging before production
5. **Update documentation**: Update any internal docs/guides

---

## Support

For issues or questions:
1. Check API docs at `/docs`
2. Review error messages in console
3. Check `MIGRATION_COMPLETE.md` for detailed information
4. Review `FASTAPI_MIGRATION_PLAN.md` for architecture details

---

**Last Updated**: 2025-10-18  
**Status**: ✅ Ready for Use  
**Framework**: FastAPI 0.119.0  
**Python**: 3.11
