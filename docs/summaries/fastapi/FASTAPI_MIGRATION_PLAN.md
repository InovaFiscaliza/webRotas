# webRotas: Flask to FastAPI Migration Plan

## Executive Summary
This document outlines a systematic approach to migrate the webRotas Flask application to FastAPI, maintaining all functionality while gaining benefits of async support, automatic API documentation, and better performance.

---

## Phase 1: Preparation & Analysis

### 1.1 Current Architecture Assessment
**Current Stack:**
- Framework: Flask 3.0.3
- Dependencies:
  - flask-cors (CORS handling)
  - flask-compress (response compression)
  - Core business logic: web_rotas.py, route_request_manager.py
  - External APIs: api_routing.py, api_elevation.py
  - Environment management: server_env.py

**Current Endpoints:**
```
GET  /                    → Redirects to /webRotas/index.html
GET  /webRotas            → Redirects to /webRotas/index.html
GET  /<path:filepath>     → Serves static files from static/
POST /process?sessionId=* → Main route processing endpoint
GET  /ok?sessionId=*      → Health check endpoint
```

**Validation Logic:**
- Request structure validation (KEYS_ROOT)
- Parameter type validation (KEYS_PARAMETERS)
- SessionId requirement validation

### 1.2 Dependencies to Replace/Update
| Flask Dependency | FastAPI Equivalent                     | Status                         |
| ---------------- | -------------------------------------- | ------------------------------ |
| flask            | fastapi                                | **Direct replacement**         |
| flask-cors       | fastapi.middleware.cors.CORSMiddleware | **Built-in**                   |
| flask-compress   | fastapi.middleware.gzip.GZIPMiddleware | **Built-in**                   |
| N/A              | uvicorn                                | **Add for ASGI server**        |
| N/A              | pydantic                               | **Add for request validation** |

### 1.3 Dependencies to Add to pyproject.toml
```toml
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

---

## Phase 2: Project Structure Refactoring

### 2.1 New Directory Structure
```
src//
├── server.py                          # → main.py (FastAPI app initialization)
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py                 # /ok endpoint
│   │   ├── static.py                 # Static file serving
│   │   └── process.py                # /process endpoint
│   └── models/
│       ├── __init__.py
│       └── requests.py               # Pydantic models for validation
├── services/
│   ├── __init__.py
│   └── route_service.py              # Business logic (refactored from controller)
├── middleware/
│   ├── __init__.py
│   └── logging.py                    # Custom logging middleware
├── config/
│   ├── __init__.py
│   ├── settings.py                   # Pydantic Settings (replaces server_env.py)
│   └── constants.py                  # KEYS_ROOT, KEYS_PARAMETERS
├── core/
│   ├── __init__.py
│   ├── exceptions.py                 # Custom exception handling
│   └── dependencies.py               # FastAPI dependency injection
│
# Existing files (minimal changes)
├── web_rotas.py
├── route_request_manager.py
├── api_routing.py
├── api_elevation.py
├── routing_servers_interface.py
├── (other utility files)
```

### 2.2 File Creation Order
1. `config/settings.py` - Settings management
2. `config/constants.py` - Request validation constants
3. `api/models/requests.py` - Pydantic validation models
4. `core/exceptions.py` - Custom exceptions
5. `core/dependencies.py` - Dependency injection utilities
6. `services/route_service.py` - Refactored controller logic
7. `api/routes/process.py` - Process endpoint
8. `api/routes/health.py` - Health check endpoint
9. `api/routes/static.py` - Static file serving
10. `middleware/logging.py` - Optional logging middleware
11. `main.py` - FastAPI app initialization (replaces server.py)

---

## Phase 3: Detailed Implementation

### 3.1 Configuration Management (Pydantic Settings)

**File: `config/settings.py`**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration from environment variables"""
    port: int = 5002
    host: str = "0.0.0.0"
    debug_mode: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**Replace:** server_env.py pattern with Pydantic Settings

### 3.2 Request Validation Models

**File: `api/models/requests.py`**
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Origin(BaseModel):
    lat: float
    lng: float
    description: str
    elevation: Optional[float] = None

class Parameters(BaseModel):
    # Base fields for all types
    pass

class ShortestParameters(Parameters):
    waypoints: List[Dict]

class CircleParameters(Parameters):
    centerPoint: Dict
    radius: float
    totalWaypoints: int

class GridParameters(Parameters):
    city: str
    state: str
    scope: str
    pointDistance: float

class OrderedParameters(Parameters):
    routeId: str
    cacheId: str
    boundingBox: Dict
    waypoints: List[Dict]

class AvoidZone(BaseModel):
    name: str
    coord: List[List[float]]

class RouteRequest(BaseModel):
    type: str = Field(..., description="Route type: shortest|circle|grid|ordered")
    origin: Origin
    parameters: Dict  # Will be validated by router
    avoidZones: Optional[List[AvoidZone]] = []
    criterion: Optional[str] = "distance"
```

### 3.3 Refactored Controller Logic

**File: `services/route_service.py`**
- Extract `controller()` function logic
- Return JSON-serializable dicts instead of Flask Response objects
- Inject dependencies (rrm, web_rotas) via dependency injection
- Maintain session_id handling and logging

### 3.4 Request Validation & Type Checking

**File: `core/dependencies.py`**
```python
from fastapi import Depends, HTTPException
from config.constants import KEYS_PARAMETERS

async def validate_parameters(
    request_type: str,
    parameters: Dict
) -> Dict:
    """Validate parameters based on request type"""
    if request_type not in KEYS_PARAMETERS:
        raise HTTPException(status_code=400, detail=f"Invalid request type")
    
    required = KEYS_PARAMETERS[request_type]
    missing = required - parameters.keys()
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing parameters: {missing}")
    
    return parameters
```

### 3.5 Route Endpoints

**File: `api/routes/process.py`**
```python
from fastapi import APIRouter, Query, Depends, HTTPException
from api.models.requests import RouteRequest
from services.route_service import process_route

router = APIRouter()

@router.post("/process")
async def process(
    session_id: str = Query(...),
    request: RouteRequest = None,
    service: RouteService = Depends()
):
    """Process route request"""
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId required")
    
    return await service.process_route(request, session_id)
```

**File: `api/routes/health.py`**
```python
from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

@router.get("/ok")
async def health_check(session_id: str = Query(...)):
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId required")
    return {"status": "ok"}
```

**File: `api/routes/static.py`**
```python
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
async def root():
    return FileResponse("static/index.html")

@router.get("/webRotas")
async def web_rotas():
    return FileResponse("static/index.html")

# Static file serving handled via StaticFiles mount
```

### 3.6 Main Application File

**File: `main.py`** (replaces server.py)
```python
import sys
import argparse
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config.settings import settings
from config.constants import KEYS_ROOT, KEYS_PARAMETERS
from api.routes import process, health
from server_env import env

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown"""
    # Startup
    try:
        args = parse_args()
        env.get_port(args.port)
        env.save_server_data()
        print(f"[webRotas] Server starting on port {env.port}")
    except Exception as e:
        print(f"[webRotas] Startup error: {e}")
    
    yield
    
    # Shutdown
    try:
        env.clean_server_data()
        print("[webRotas] Server shutdown")
    except Exception as e:
        print(f"[webRotas] Cleanup error: {e}")

# Create FastAPI app
app = FastAPI(
    title="webRotas",
    description="Vehicle route management for ANATEL inspection activities",
    version="0.1.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Include routers
app.include_router(process.router)
app.include_router(health.router)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/webRotas", StaticFiles(directory=str(static_path), html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/webRotas")
async def web_rotas_redirect():
    return FileResponse("static/index.html")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WebRotas Server")
    parser.add_argument("--port", type=int, default=env.port, help="Server port")
    parser.add_argument("--debug", type=bool, default=env.debug_mode, help="Debug mode")
    
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            print(f"[webRotas] Warning: Unknown arguments ignored: {unknown}")
        return args
    except Exception as e:
        print(f"[webRotas] Error parsing arguments: {e}")
        return argparse.Namespace(port=env.port, debug=env.debug_mode)

if __name__ == "__main__":
    import uvicorn
    args = parse_args()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.debug
    )
```

---

## Phase 4: Migration Steps

### Step 1: Update pyproject.toml
- Add FastAPI, Uvicorn, Pydantic dependencies
- Keep existing business logic dependencies
- Update to use `uv sync` with new deps

### Step 2: Create New Directory Structure
- Create `/api`, `/config`, `/services`, `/core`, `/middleware` directories
- Create `__init__.py` files in each

### Step 3: Implement Configuration & Constants
- `config/settings.py`
- `config/constants.py`
- `core/exceptions.py`

### Step 4: Create Pydantic Models
- `api/models/requests.py` with all validation models
- Test validation with sample payloads

### Step 5: Implement Route Endpoints
- `api/routes/process.py`
- `api/routes/health.py`
- Migrate validation logic to dependencies

### Step 6: Refactor Business Logic
- Extract controller logic → `services/route_service.py`
- Keep all web_rotas, route_request_manager logic intact
- Add dependency injection

### Step 7: Create Main Application
- `main.py` with FastAPI setup
- Configure CORS, GZIP, static files, lifespan

### Step 8: Testing & Validation
- Test all endpoints with existing JSON payloads
- Verify CLI client still works
- Load test with same request patterns
- Validate static file serving

### Step 9: Documentation & Cleanup
- Generate OpenAPI docs (automatic at `/docs`)
- Update README.md with FastAPI commands
- Remove old server.py file
- Update development workflow docs

---

## Phase 5: Testing Strategy

### 5.1 Manual Testing
```bash
# Health check
curl "http://127.0.0.1:5002/ok?sessionId=test"

# Process request (use existing test payloads)
uv run src/ucli/webrota_client.py tests/request_shortest*.json

# Static file serving
curl "http://127.0.0.1:5002/"
curl "http://127.0.0.1:5002/webRotas/index.html"
```

### 5.2 Automated Testing
- Keep existing test structure in `tests/`
- Adapt CLI client if needed
- Compare response formats between Flask and FastAPI
- Load testing with concurrent requests

### 5.3 Performance Benchmarking
- Compare response times (Flask vs FastAPI)
- Test concurrent request handling
- Monitor memory usage
- Stress test with high request volumes

---

## Phase 6: Deployment & Verification

### 6.1 Production Server
Replace Flask development server with Uvicorn:
```bash
# Development
uvicorn main:app --reload --port 5002

# Production (use process manager like supervisor or systemd)
uvicorn main:app --host 0.0.0.0 --port 5002 --workers 4
```

### 6.2 Environment Compatibility
- Ensure WSL/Linux compatibility maintained
- Test container integration (Podman/OSRM)
- Verify static asset serving for web interface

### 6.3 Rollback Plan
- Keep Flask version tagged in git
- Maintain server.py as fallback
- Version lock dependencies in pyproject.toml

---

## Migration Checklist

- [ ] **Phase 1 Complete**: Dependencies identified, current architecture documented
- [ ] **Phase 2 Complete**: Directory structure created
- [ ] **Phase 3 Complete**: All configuration files created
- [ ] **Phase 3 Complete**: Pydantic models defined and tested
- [ ] **Phase 3 Complete**: Route endpoints implemented
- [ ] **Phase 3 Complete**: Business logic refactored
- [ ] **Phase 3 Complete**: Main application file created
- [ ] **Phase 4 Step 1**: pyproject.toml updated
- [ ] **Phase 4 Step 2-7**: All files created and integrated
- [ ] **Phase 5**: All tests passing
- [ ] **Phase 5**: Performance benchmarks acceptable
- [ ] **Phase 6**: Deployment tested in staging
- [ ] **Phase 6**: Documentation updated
- [ ] **Production**: Deploy and monitor

---

## Key Benefits of FastAPI

1. **Async Support**: Better handling of concurrent requests
2. **Automatic Documentation**: OpenAPI/Swagger at `/docs`
3. **Type Validation**: Pydantic ensures data integrity
4. **Better Performance**: Comparable or better than Flask
5. **Developer Experience**: Better error messages, IDE support
6. **Dependency Injection**: Built-in, cleaner code organization
7. **Standards-based**: OpenAPI 3.0 compliant

---

## Potential Challenges & Mitigations

| Challenge                               | Mitigation                                                     |
| --------------------------------------- | -------------------------------------------------------------- |
| Breaking changes in request handling    | Comprehensive validation layer, run tests against old payloads |
| Static file serving differences         | Use StaticFiles middleware, test thoroughly                    |
| CORS/compression compatibility          | Use built-in middleware, verify configuration                  |
| CLI client compatibility                | Update if needed, ensure JSON format unchanged                 |
| Async compatibility with business logic | Wrap sync operations if needed, use `run_in_executor`          |
| Port configuration handling             | Use Pydantic Settings + environment variables                  |

---

## Timeline Estimate

- **Phase 1-2**: 2-4 hours (planning & structure)
- **Phase 3**: 4-6 hours (implementation)
- **Phase 4**: 4-6 hours (integration & testing)
- **Phase 5**: 3-4 hours (comprehensive testing)
- **Phase 6**: 2-3 hours (deployment & verification)

**Total: 15-23 hours of development time**

---

## Rollback Strategy

If issues arise during migration:
1. Keep Flask branch available for quick rollback
2. Use feature flags for gradual deployment
3. Run FastAPI and Flask in parallel initially
4. Monitor logs for errors before full cutover
