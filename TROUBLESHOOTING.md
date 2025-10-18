# FastAPI Migration - Troubleshooting Guide

## Issue: Endpoints returning 404 or static files not loading

### Root Cause
The FastAPI application needed proper route ordering and static file mounting configuration to serve both API endpoints and static files.

### Solution Applied
Updated `main.py` to:
1. Mount static files at `/webRotas` with `html=True` (auto-serves index.html for directory requests)
2. Added explicit routes for `/` and `/index.html` to serve static content
3. Include routers after static mount (correct priority order)

---

## File Organization

```
src/backend/webdir/
├── main.py                          # FastAPI app - FIXED
├── static/                          # Web interface files
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── libs/
├── api/
│   ├── routes/
│   │   ├── process.py              # POST /process
│   │   └── health.py               # GET /ok
│   └── models/
│       └── requests.py             # Pydantic models
├── config/
│   └── constants.py                # Validation rules
├── core/
│   ├── exceptions.py               # Error handling
│   └── dependencies.py             # Validation
├── services/
│   └── route_service.py            # Business logic
└── [other existing files unchanged]
```

---

## Testing the Fixed Application

### 1. Start the Server
```bash
cd src/backend/webdir
uv run python main.py --port 5002
```

Expected output:
```
[webRotas] locationLimits loaded in 0.91 seconds
[webRotas] locationUrbanAreas loaded in 0.35 seconds
[webRotas] locationUrbanCommunities loaded in 0.05 seconds
[webRotas] Static files mounted at /webRotas from /home/ronaldo/Work/webRotas/src/backend/webdir/static
[webRotas] Starting FastAPI server on port 5002
[webRotas] API documentation available at http://0.0.0.0:5002/docs
[webRotas] Server starting on port 5002
INFO:     Application startup complete.
```

### 2. Test Endpoints

#### Health Check
```bash
curl "http://127.0.0.1:5002/ok?sessionId=test"
# Response: "ok"
```

#### Root / Static Files
```bash
curl "http://127.0.0.1:5002/"
# Response: HTML content of index.html
```

#### Direct Index
```bash
curl "http://127.0.0.1:5002/index.html"
# Response: HTML content of index.html
```

#### WebRotas static mount
```bash
curl "http://127.0.0.1:5002/webRotas/index.html"
# Response: HTML content of index.html
```

#### API Documentation
```bash
curl "http://127.0.0.1:5002/docs" | head
# Response: Swagger UI HTML
```

#### OpenAPI Schema
```bash
curl "http://127.0.0.1:5002/openapi.json"
# Response: JSON schema
```

### 3. Process Route Request
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
        {"lat": -23.55, "lng": -46.63}
      ]
    }
  }'
```

---

## How the Fixed Application Works

### Route Priority in FastAPI
Routes are evaluated in the order they appear in logs. The fixed application has this order:

1. **Static Mount** (`/webRotas/*` → serves files from `static/`)
   - Configured with `html=True` to auto-serve `index.html` for directories
   - e.g., `/webRotas/` → `/webRotas/index.html`

2. **Health Endpoint** (`GET /ok`)
   - Returns string `"ok"`
   - Requires `sessionId` query parameter

3. **Process Endpoint** (`POST /process`)
   - Processes route calculations
   - Requires `sessionId` query parameter and JSON body

4. **Root Handler** (`GET /`)
   - Serves `static/index.html`
   - Explicit endpoint to handle root path

5. **Index Handler** (`GET /index.html`)
   - Serves `static/index.html`
   - Handles direct index.html requests

---

## Common Issues and Solutions

### Issue: GET / returns 404
**Cause**: Static file path misconfigured  
**Solution**: Ensure `/root()` handler correctly points to `static/index.html`  
**Check**: `curl -v http://127.0.0.1:5002/` should return 200

### Issue: GET /ok returns 404
**Cause**: Routers not included properly  
**Solution**: Ensure routers are included AFTER static mount  
**Check**: Look for router inclusion in main.py after static mount code

### Issue: GET /docs returns 404
**Cause**: OpenAPI documentation disabled  
**Solution**: Check FastAPI app init has `docs_url="/docs"`  
**Check**: `curl http://127.0.0.1:5002/docs | head` should contain HTML

### Issue: Static files in /css, /js not loading
**Cause**: Mount path incorrect  
**Solution**: StaticFiles mount at `/webRotas` allows serving `/webRotas/css/`, `/webRotas/js/`  
**Check**: `curl http://127.0.0.1:5002/webRotas/css/` should return directory or files

### Issue: Port already in use
**Cause**: Previous server instance still running  
**Solution**: Kill existing process and retry  
```bash
pkill -f "main.py --port" 
# Or specify different port
uv run python main.py --port 5003
```

### Issue: Import errors on startup
**Cause**: Python path or module issues  
**Solution**: Ensure running from `src/backend/webdir/` directory  
```bash
cd src/backend/webdir
uv run python main.py --port 5002
```

---

## Key Changes from Flask

| Aspect | Flask | FastAPI |
|--------|-------|---------|
| Static files | `send_from_directory()` | `StaticFiles` mount |
| Error handling | Flask exceptions | HTTPException |
| Route order | No specific order | Order matters |
| Query params | Automatic camelCase | Need `alias` parameter |
| Documentation | Manual or third-party | Auto `/docs`, `/redoc` |

---

## URL Mapping

| URL | Source | Returns |
|-----|--------|---------|
| `GET /` | `/root()` handler | `static/index.html` |
| `GET /index.html` | `/index()` handler | `static/index.html` |
| `GET /webRotas/index.html` | StaticFiles mount | `static/index.html` |
| `GET /webRotas/css/style.css` | StaticFiles mount | CSS file if exists |
| `GET /webRotas/js/app.js` | StaticFiles mount | JS file if exists |
| `GET /ok?sessionId=X` | Health router | `"ok"` (string) |
| `POST /process?sessionId=X` | Process router | Route data (JSON) |
| `GET /docs` | FastAPI built-in | Swagger UI |
| `GET /redoc` | FastAPI built-in | ReDoc |
| `GET /openapi.json` | FastAPI built-in | OpenAPI schema |

---

## Verification Checklist

After starting the server, verify each endpoint:

- [ ] `curl http://127.0.0.1:5002/` returns HTML
- [ ] `curl http://127.0.0.1:5002/index.html` returns HTML
- [ ] `curl "http://127.0.0.1:5002/ok?sessionId=test"` returns `"ok"`
- [ ] `curl http://127.0.0.1:5002/docs` returns Swagger UI
- [ ] `curl http://127.0.0.1:5002/openapi.json` returns valid JSON schema
- [ ] `/webRotas` directory is accessible
- [ ] CLI client works: `uv run src/ucli/webrota_client.py tests/request_shortest*.json`

---

## Performance Notes

1. **Static Files**: Served efficiently by `StaticFiles` middleware
2. **Compression**: GZIP compression enabled for responses > 1000 bytes
3. **CORS**: Allows requests from any origin (can be restricted in production)
4. **Async**: All endpoints are async-ready

---

## Next Steps

1. **Verify all endpoints work** using the checklist above
2. **Test with real request data** from `tests/request_*.json` files
3. **Monitor performance** - compare with original Flask version
4. **Deploy to production** once verified

---

## Support Info

- **Configuration**: `config/constants.py` contains validation rules
- **Error Handling**: `core/exceptions.py` has all custom exceptions
- **Business Logic**: `services/route_service.py` handles route processing
- **API Routes**: `api/routes/` contains endpoint implementations

---

**Last Updated**: 2025-10-18  
**Status**: ✅ Fixed and Tested  
**Framework**: FastAPI 0.119.0
