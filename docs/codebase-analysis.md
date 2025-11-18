# webRotas Codebase Organization Analysis

## Executive Summary

The current codebase structure suffers from **poor separation of concerns**, **mixed responsibility levels**, and **unclear module hierarchy**. Modules at the same level handle vastly different responsibilities (domain logic, infrastructure, utilities), making it difficult to understand data flow and maintain clean dependencies.

---

## Current Structure Issues

### 1. **Flat Module Organization** ⚠️

**Problem**: All business logic modules sit at the same level despite handling different concerns:

```
src/webrotas/
├── rotas.py                        # Domain: Route processing
├── api_routing.py                  # Infrastructure: OSRM integration + domain logic
├── zone_aware_routing.py           # Domain: Zone-aware routing logic
├── segment_alternatives.py         # Domain: Alternative routing
├── iterative_matrix_builder.py     # Infrastructure: Matrix building
├── api_elevation.py                # Infrastructure: Elevation API
├── shapefiles.py                   # Infrastructure: Geospatial data access
├── regions.py                      # Utilities: Region calculations
├── geojson_converter.py            # Utilities: Format conversion
├── lua_converter.py                # Utilities: Lua format conversion
├── version_manager.py              # Utilities: Version management
├── server_env.py                   # Configuration
└── api/
    ├── routes/
    │   ├── process.py              # Endpoint
    │   └── health.py               # Endpoint
    ├── models/
    │   └── requests.py             # DTO/Schemas
    └── __init__.py
```

**Impact**: 
- 11 root modules with mixed concerns create cognitive overhead
- No clear pattern for where new code should go
- Hard to distinguish domain logic from technical infrastructure

---

### 2. **Unclear Responsibility Boundaries**

#### **`api_routing.py` - Major Offender**
This 600+ line module conflates multiple concerns:

```python
# Line 78-112: Client-side avoid zones processing (domain)
def process_avoidzones(geojson: dict) -> None: ...

# Line 115-153: Spatial indexing (infrastructure utility)
def load_spatial_index(geojson) -> tuple: ...

# Line 156-224: Route-zone intersection analysis (domain)
def check_route_intersections(...) -> Dict: ...

# Line ~250+: OSRM API integration (infrastructure)
async def request_osrm(...) -> dict: ...

# Line ~400+: OR-Tools TSP solving (domain algorithm)
def optimize_route_with_ortools(...) -> List: ...
```

**Why it's problematic**:
- Changes to OSRM integration require understanding spatial indexing logic
- Zone analysis is buried with API plumbing
- Difficult to test domain logic in isolation

#### **`rotas.py` - Processor Class**
While better structured, it depends on scattered functions:

```python
# Imports from multiple layers:
from webrotas.api_routing import compute_bounding_box, calculate_optimal_route
from webrotas.api_elevation import enrich_waypoints_with_elevation
from webrotas.domain.geospatial.regions import ...  # region calculations
import webrotas.shapefiles as sf
```

This shows the processor must know about multiple infrastructure/utility modules.

---

### 3. **Import Chains & Hidden Dependencies**

```
process_route (service layer)
  └─> RouteProcessor (business layer)
       ├─> calculate_optimal_route (api_routing.py - infrastructure)
       │    ├─> request_osrm (infrastructure - OSRM)
       │    ├─> get_alternatives_for_multipoint_route (segment_alternatives - domain)
       │    └─> find_route_around_zones (zone_aware_routing - domain)
       ├─> enrich_waypoints_with_elevation (api_elevation - infrastructure)
       └─> get_polyline_comunities (shapefiles - data access)
            └─> ensure_shapefile_exists (shapefiles - resource management)
```

**Issues**:
- Long dependency chains obscure data flow
- Difficult to trace what a function really needs
- Layering is not enforced; API code can import domain directly

---

### 4. **Naming Inconsistencies** 🏷️

| Module | Pattern | Problem |
|--------|---------|---------|
| `api_routing.py` | `api_*` | Suggests it's an API endpoint, but it's infrastructure |
| `api_elevation.py` | `api_*` | Same confusion |
| `rotas.py` | Portuguese name | Inconsistent with English file names |
| `regions.py` | Generic utility | Unclear what it does |
| `shapefiles.py` | Generic utility | Vague; should indicate "geospatial data access" |

---

### 5. **Misplaced Responsibilities**

| Code | Current Location | Should Be |
|------|------------------|-----------|
| `RouteProcessor` class | `rotas.py` | `core/processors.py` or `domain/route_processor.py` |
| OSRM integration | `api_routing.py` | `infrastructure/routing/osrm.py` |
| Avoid zones processing | `api_routing.py` | `domain/avoid_zones.py` |
| Zone-aware routing logic | `zone_aware_routing.py` | `domain/routing/zone_aware.py` |
| Spatial indexing | `api_routing.py` | `infrastructure/spatial/index.py` |
| Matrix building | `iterative_matrix_builder.py` | `infrastructure/routing/matrix_builder.py` |
| Geospatial data loading | `shapefiles.py` | `infrastructure/geospatial/shapefiles.py` |
| Region utilities | `regions.py` | `infrastructure/geospatial/regions.py` |

---

### 6. **Weak API Layer Organization**

```
api/
├── routes/           # Endpoints (good)
├── models/           # DTOs (minimal structure)
└── (no middleware, exceptions, utils)
```

**Missing**: Dedicated exception handlers, middleware, validators separate from routes.

---

### 7. **Configuration Scattered**

```
config/
├── server_hosts.py       # Server URLs
├── constants.py          # Constants
└── logging_config.py     # Logging setup

Orphaned configs:
├── server_env.py         # Server runtime environment
├── version_manager.py    # (not really config, but version handling)
```

`server_env.py` mixes environment management with state (should be in config/).

---

### 8. **Missing Module Structure**

**Utilities have no clear home**:
- `geojson_converter.py` - Floating utility
- `lua_converter.py` - Floating utility
- `version_manager.py` - Floating utility
- Format converters should group together

---

## Recommended New Structure

```
src/webrotas/
│
├── core/                           # Application core (config, exceptions, base classes)
│   ├── __init__.py
│   ├── exceptions.py               # Unified exception hierarchy
│   ├── dependencies.py             # FastAPI dependencies
│   └── logger.py                   # Logging setup
│
├── config/                         # Configuration & environment
│   ├── __init__.py
│   ├── constants.py                # App constants
│   ├── server_hosts.py             # Server URL configuration
│   ├── server_env.py               # Runtime environment management
│   └── logging_config.py           # Logging configuration
│
├── domain/                         # Business logic (no external dependencies except data types)
│   ├── __init__.py
│   ├── models.py                   # Domain models (UserData, RouteProcessor, etc.)
│   ├── routing/
│   │   ├── __init__.py
│   │   ├── processor.py            # RouteProcessor class
│   │   ├── zone_aware.py           # Zone-aware routing logic
│   │   └── alternatives.py         # Segment-based alternatives logic
│   ├── avoid_zones/
│   │   ├── __init__.py
│   │   ├── models.py               # Zone data structures
│   │   ├── processor.py            # Zone processing logic
│   │   └── spatial.py              # Spatial indexing & intersection checks
│   └── geospatial/
│       ├── __init__.py
│       ├── bounding_box.py         # Bounding box calculations
│       └── regions.py              # Region utilities
│
├── infrastructure/                 # Technical integrations & external services
│   ├── __init__.py
│   ├── routing/
│   │   ├── __init__.py
│   │   ├── osrm.py                 # OSRM API client
│   │   └── matrix_builder.py       # Iterative matrix building
│   ├── elevation/
│   │   ├── __init__.py
│   │   └── service.py              # Elevation API integration
│   └── geospatial/
│       ├── __init__.py
│       ├── shapefiles.py           # Shapefile data access
│       └── loaders.py              # Data loading utilities
│
├── api/                            # API layer (FastAPI)
│   ├── __init__.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handlers.py       # Exception handlers
│   │   └── validators.py           # Request validation middleware
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py             # Request DTOs
│   │   └── responses.py            # Response DTOs
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── process.py              # /process endpoint
│   │   └── health.py               # /health endpoint
│   └── services/
│       ├── __init__.py
│       └── route_service.py        # Route processing service
│
├── utils/                          # Cross-cutting utilities
│   ├── __init__.py
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── geojson.py
│   │   └── lua.py
│   ├── versioning/
│   │   ├── __init__.py
│   │   └── version_manager.py
│   └── cache/
│       ├── __init__.py
│       ├── polylines.py
│       ├── routes.py
│       └── bounding_boxes.py
│
├── main.py                         # Application entry point
└── __init__.py
```

---

## Migration Strategy

### Phase 1: Prepare Foundation
1. Create new directory structure
2. Create `__init__.py` files with proper exports
3. Create a dependency map (which modules depend on which)

### Phase 2: Move Domain Logic
1. Move `rotas.py` → `domain/routing/processor.py` (rename class as needed)
2. Move `zone_aware_routing.py` → `domain/routing/zone_aware.py`
3. Move `segment_alternatives.py` → `domain/routing/alternatives.py`
4. Extract avoid zones logic → `domain/avoid_zones/processor.py`
5. Extract spatial indexing → `domain/avoid_zones/spatial.py`
6. Move region calculations → `domain/geospatial/regions.py`

### Phase 3: Move Infrastructure
1. Extract OSRM client from `api_routing.py` → `infrastructure/routing/osrm.py`
2. Extract matrix builder → `infrastructure/routing/matrix_builder.py` (rename module)
3. Move `api_elevation.py` → `infrastructure/elevation/service.py`
4. Move `shapefiles.py` → `infrastructure/geospatial/shapefiles.py`

### Phase 4: Move Utilities
1. Move converters → `utils/converters/`
2. Move `version_manager.py` → `utils/versioning/`
3. Keep cache modules where they are (already well-organized)

### Phase 5: Update API Layer
1. Keep existing endpoints
2. Move validation logic to `api/middleware/`
3. Move service logic to `api/services/`

### Phase 6: Fix Imports
1. Update all imports throughout codebase
2. Ensure clean dependency directions (no circular imports)
3. Run import cycle detection

---

## Import Rules After Refactoring

✅ **Allowed**:
```python
# API layer can import from all layers
from domain import RouteProcessor
from infrastructure import OSRMClient
from utils import converters

# Domain can only import domain
from domain.routing import processor
from domain.geospatial import regions

# Infrastructure can import domain (for types)
from domain.models import UserData

# Utils can import nothing (pure utilities)
```

❌ **Forbidden**:
```python
# Domain importing infrastructure
from infrastructure.routing import OSRMClient  # NO!

# Circular imports
domain -> infrastructure -> domain  # NO!

# Infrastructure importing API
from api.routes import process  # NO!
```

---

## Expected Benefits

| Issue | Before | After |
|-------|--------|-------|
| **Number of root modules** | 11 mixed concerns | 3 layers (domain, infrastructure, api) |
| **Module clarity** | Unclear responsibility | Clear layer + feature-based grouping |
| **New feature location** | "Where do I put this?" | Clear: domain/ or infrastructure/ |
| **Testability** | Hard to mock infrastructure | Easy: inject infrastructure dependencies |
| **Code reuse** | Duplicate logic in multiple files | Centralized in domain/ |
| **Import chains** | 5-7 levels deep | 2-3 levels maximum |
| **Maintenance** | High cognitive load | Reduced: each module has one job |

---

## Implementation Notes

1. **Gradual migration**: Move modules one at a time, updating imports in a controlled manner
2. **Test coverage**: Ensure tests pass after each phase
3. **Backwards compatibility**: Create compatibility imports in old locations during transition (optional)
4. **Documentation**: Update WARP.md with new structure diagram
5. **CI/CD**: Add linting rules to prevent cross-layer imports

---

## Files to Create/Modify

### New Directories
- `domain/`
- `domain/routing/`
- `domain/avoid_zones/`
- `domain/geospatial/`
- `infrastructure/`
- `infrastructure/routing/`
- `infrastructure/elevation/`
- `infrastructure/geospatial/`
- `utils/`
- `utils/converters/`
- `utils/versioning/`
- `api/middleware/`
- `api/services/`

### Files to Move/Rename
- See migration strategy (Phase 1-6)

### Files to Update (imports)
- All `.py` files in `tests/`
- `main.py`
- All files in `api/routes/`
- `ucli/webrota_client.py` (if applicable)
