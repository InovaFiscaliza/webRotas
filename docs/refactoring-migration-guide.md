# webRotas Refactoring Migration Guide

## File Movement Mapping

### PHASE 1: Create Directory Structure

```bash
mkdir -p src/webrotas/domain/{routing,avoid_zones,geospatial}
mkdir -p src/webrotas/infrastructure/{routing,elevation,geospatial}
mkdir -p src/webrotas/utils/{converters,versioning,cache}
mkdir -p src/webrotas/api/{middleware,services}
mkdir -p src/webrotas/core
```

### PHASE 2: Move Domain Logic

| Source | Destination | Rename? | Notes |
|--------|-------------|---------|-------|
| `rotas.py` | `domain/routing/processor.py` | Class stays `RouteProcessor` | Core routing logic |
| `zone_aware_routing.py` | `domain/routing/zone_aware.py` | No | Zone-aware routing algorithms |
| `segment_alternatives.py` | `domain/routing/alternatives.py` | No | Segment-based alternatives |
| `regions.py` | `domain/geospatial/regions.py` | No | Region calculations |
| Extract from `api_routing.py` | `domain/avoid_zones/processor.py` | Extract functions | Avoid zones processing |
| Extract from `api_routing.py` | `domain/avoid_zones/spatial.py` | Extract functions | Spatial indexing & intersections |

### PHASE 3: Move Infrastructure

| Source | Destination | Rename? | Notes |
|--------|-------------|---------|-------|
| Extract from `api_routing.py` | `infrastructure/routing/osrm.py` | Extract functions | OSRM API client |
| `iterative_matrix_builder.py` | `infrastructure/routing/matrix_builder.py` | No | Rename file only |
| `api_elevation.py` | `infrastructure/elevation/service.py` | No | Rename file only |
| `shapefiles.py` | `infrastructure/geospatial/shapefiles.py` | No | Rename file only |

### PHASE 4: Move Utilities

| Source | Destination | Rename? | Notes |
|--------|-------------|---------|-------|
| `geojson_converter.py` | `utils/converters/geojson.py` | No | GeoJSON conversion |
| `lua_converter.py` | `utils/converters/lua.py` | No | Lua format conversion |
| `version_manager.py` | `utils/versioning/version_manager.py` | No | Version tracking |
| `cache/polylines.py` | `utils/cache/polylines.py` | No | Already well-placed |
| `cache/routes.py` | `utils/cache/routes.py` | No | Already well-placed |
| `cache/bounding_boxes.py` | `utils/cache/bounding_boxes.py` | No | Already well-placed |

### PHASE 5: Move API Layer Components

| Source | Destination | Rename? | Notes |
|--------|-------------|---------|-------|
| Validators from `api/routes/process.py` | `api/middleware/validators.py` | Extract | Request validation |
| Error handlers from core | `api/middleware/error_handlers.py` | Create | Exception handling |
| `services/route_service.py` | `api/services/route_service.py` | Move | Service layer |

### PHASE 6: Move/Update Core Components

| Source | Destination | Rename? | Notes |
|--------|-------------|---------|-------|
| `core/exceptions.py` | `core/exceptions.py` | Keep | Already in core |
| `core/dependencies.py` | `core/dependencies.py` | Keep | Already in core |
| Move `config/logging_config.py` → `core/logger.py` | Optional | Better grouping |

### Files to Keep (Already Well-Organized)

- `main.py` - Application entry point (at root)
- `server_env.py` - Move to `config/` 
- `config/constants.py` - Already good
- `config/server_hosts.py` - Already good
- `api/routes/process.py` - Keep, update imports
- `api/routes/health.py` - Keep, update imports
- `api/models/requests.py` - Keep, update imports

---

## Import Transformation Patterns

### Pattern 1: Moving RouteProcessor to domain/routing/

**Before:**
```python
from webrotas.rotas import RouteProcessor
```

**After:**
```python
from webrotas.domain.routing.processor import RouteProcessor
```

**Files affected:**
- `api/routes/process.py`
- `api/services/route_service.py`
- All test files importing RouteProcessor

---

### Pattern 2: OSRM Integration Extraction

**Before:**
```python
# In api_routing.py
async def calculate_optimal_route(...):
    osrm_response = await request_osrm(...)
    ...

async def request_osrm(request_type, coordinates, params):
    # Direct OSRM API calls
    ...
```

**After:**
```python
# In infrastructure/routing/osrm.py
class OSRMClient:
    async def request_osrm(self, request_type, coordinates, params):
        # OSRM API calls
        ...
    
    async def calculate_optimal_route(self, ...):
        # Route calculation using OSRM
        ...

# In domain/routing/processor.py
async def process_shortest(self, ...):
    osrm_client = OSRMClient()  # Injected or created
    result = await osrm_client.calculate_optimal_route(...)
```

---

### Pattern 3: Avoid Zones Extraction

**Before:**
```python
# In api_routing.py (mixed with OSRM code)
def process_avoidzones(geojson: dict) -> None: ...
def load_spatial_index(geojson: Dict) -> tuple: ...
def check_route_intersections(coords, polygons, tree) -> Dict: ...
```

**After:**
```python
# In domain/avoid_zones/processor.py
def process_avoidzones(geojson: dict) -> None: ...

# In domain/avoid_zones/spatial.py
def load_spatial_index(geojson: Dict) -> tuple: ...
def check_route_intersections(coords, polygons, tree) -> Dict: ...

# Updated imports in domain/routing/processor.py
from webrotas.domain.avoid_zones.processor import process_avoidzones
from webrotas.domain.avoid_zones.spatial import load_spatial_index, check_route_intersections
```

---

### Pattern 4: Infrastructure Dependency Injection

**Before:**
```python
# In rotas.py
async def process_shortest(self, ...):
    origin, waypoints, paths = await calculate_optimal_route(
        self.origin, waypoints, self.criterion, self.avoid_zones
    )
```

**After:**
```python
# In domain/routing/processor.py
from webrotas.infrastructure.routing.osrm import OSRMClient

class RouteProcessor:
    def __init__(self, ..., osrm_client: OSRMClient = None):
        self.osrm_client = osrm_client or OSRMClient()
    
    async def process_shortest(self, ...):
        origin, waypoints, paths = await self.osrm_client.calculate_optimal_route(
            self.origin, waypoints, self.criterion, self.avoid_zones
        )
```

---

### Pattern 5: Geospatial Data Access

**Before:**
```python
# In rotas.py
import webrotas.shapefiles as sf
from webrotas.regions import extrair_bounding_box_de_regioes

location_limits, location_urban_areas = get_areas_urbanas_cache(city, state)
```

**After:**
```python
# In domain/routing/processor.py
from webrotas.infrastructure.geospatial.shapefiles import get_areas_urbanas_cache
from webrotas.domain.geospatial.regions import extrair_bounding_box_de_regioes

location_limits, location_urban_areas = get_areas_urbanas_cache(city, state)
```

---

### Pattern 6: Utilities Usage

**Before:**
```python
from webrotas.geojson_converter import avoid_zones_to_geojson
from webrotas.lua_converter import write_lua_zones_file
from webrotas.version_manager import save_version
```

**After:**
```python
from webrotas.utils.converters.geojson import avoid_zones_to_geojson
from webrotas.utils.converters.lua import write_lua_zones_file
from webrotas.utils.versioning.version_manager import save_version
```

---

## Detailed File Extraction Guide

### Extracting OSRM Integration from api_routing.py

**Step 1: Identify functions to move**
```python
# Functions to move to infrastructure/routing/osrm.py:
- request_osrm()
- _make_osrm_request()
- calculate_optimal_route()
- optimize_route_with_ortools()
```

**Step 2: Create infrastructure/routing/osrm.py**
```python
"""OSRM routing service integration"""

import os
from typing import Dict, List, Tuple, Any, Optional
import httpx
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from webrotas.config.logging_config import get_logger
from webrotas.config.server_hosts import get_osrm_url

logger = get_logger(__name__)

# Constants from api_routing.py that relate to OSRM
TIMEOUT = 10
ALTERNATIVES = 3
OSRM_URL = os.getenv("OSRM_URL", "http://localhost:5000")

class OSRMClient:
    def __init__(self, osrm_url: str = None):
        self.osrm_url = osrm_url or OSRM_URL
    
    async def request_osrm(self, request_type: str, coordinates: str, params: dict = None) -> dict:
        """Make request to OSRM server"""
        # Implementation moved from api_routing.py
        ...
    
    async def calculate_optimal_route(self, origin, waypoints, criterion, avoid_zones):
        """Calculate optimal route using OSRM"""
        # Implementation moved from api_routing.py
        ...
    
    def optimize_route_with_ortools(self, distances, durations, ...):
        """Optimize using OR-Tools TSP solver"""
        # Implementation moved from api_routing.py
        ...
```

**Step 3: Update imports in domain/routing/processor.py**
```python
# Old:
from webrotas.api_routing import calculate_optimal_route

# New:
from webrotas.infrastructure.routing.osrm import OSRMClient

# Usage:
osrm_client = OSRMClient()
origin, waypoints, paths = await osrm_client.calculate_optimal_route(...)
```

---

### Extracting Spatial Indexing from api_routing.py

**Step 1: Create domain/avoid_zones/spatial.py**
```python
"""Spatial indexing and intersection analysis for avoid zones"""

from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import LineString, shape
from shapely.strtree import STRtree
from webrotas.config.logging_config import get_logger

logger = get_logger(__name__)

def load_spatial_index(geojson: Dict[str, Any]) -> Tuple[List, Optional[STRtree]]:
    """Build spatial index from GeoJSON"""
    # Implementation moved from api_routing.py
    ...

def check_route_intersections(coords: List[List[float]], polygons: List, tree: Optional[STRtree]) -> Dict[str, Any]:
    """Calculate route-polygon intersections"""
    # Implementation moved from api_routing.py
    ...
```

**Step 2: Update imports in domain/avoid_zones/processor.py**
```python
from webrotas.domain.avoid_zones.spatial import load_spatial_index, check_route_intersections
```

---

### Extracting Avoid Zones Processing from api_routing.py

**Step 1: Create domain/avoid_zones/processor.py**
```python
"""Avoid zones processing and management"""

import json
from pathlib import Path
from typing import Dict, Any
from webrotas.config.logging_config import get_logger
from webrotas.utils.converters.geojson import avoid_zones_to_geojson
from webrotas.utils.converters.lua import write_lua_zones_file
from webrotas.utils.versioning.version_manager import save_version

logger = get_logger(__name__)

def process_avoidzones(geojson: dict, history_dir: Path, lua_zones_file: Path, latest_polygons: Path) -> None:
    """Process avoid zones and save to history"""
    # Implementation moved from api_routing.py
    ...
```

---

## __init__.py Files to Create

### src/webrotas/domain/__init__.py
```python
"""Domain layer - core business logic"""

from .routing.processor import RouteProcessor
from .avoid_zones.processor import process_avoidzones
from .geospatial.regions import (
    extrair_bounding_box_de_regioes,
    is_region_inside_another,
    compare_regions_without_bounding_box,
)

__all__ = [
    "RouteProcessor",
    "process_avoidzones",
    "extrair_bounding_box_de_regioes",
    "is_region_inside_another",
    "compare_regions_without_bounding_box",
]
```

### src/webrotas/domain/routing/__init__.py
```python
"""Routing domain logic"""

from .processor import RouteProcessor
from .zone_aware import (
    generate_boundary_waypoints,
    find_route_around_zones,
)
from .alternatives import SegmentAlternativesBuilder

__all__ = [
    "RouteProcessor",
    "generate_boundary_waypoints",
    "find_route_around_zones",
    "SegmentAlternativesBuilder",
]
```

### src/webrotas/infrastructure/__init__.py
```python
"""Infrastructure layer - external integrations"""

from .routing.osrm import OSRMClient
from .routing.matrix_builder import IterativeMatrixBuilder
from .elevation.service import enrich_waypoints_with_elevation
from .geospatial.shapefiles import (
    ensure_shapefile_exists,
    ensure_all_shapefiles,
)

__all__ = [
    "OSRMClient",
    "IterativeMatrixBuilder",
    "enrich_waypoints_with_elevation",
    "ensure_shapefile_exists",
    "ensure_all_shapefiles",
]
```

### src/webrotas/utils/__init__.py
```python
"""Utilities - cross-cutting concerns"""

from .converters.geojson import avoid_zones_to_geojson
from .converters.lua import write_lua_zones_file
from .versioning.version_manager import save_version

__all__ = [
    "avoid_zones_to_geojson",
    "write_lua_zones_file",
    "save_version",
]
```

---

## Import Update Checklist

### Files that need import updates:

- [ ] `main.py` - Update main.py imports
- [ ] `api/routes/process.py` - Route endpoint imports
- [ ] `api/routes/health.py` - Health endpoint imports
- [ ] `api/services/route_service.py` - Service imports
- [ ] `api/models/requests.py` - Model imports
- [ ] `core/dependencies.py` - Dependency imports
- [ ] `config/server_hosts.py` - Config imports (if any)
- [ ] `tests/test_*.py` - All test files

### Test files to update:

```bash
tests/
├── test_enhanced_routing.py
├── test_logging.py
├── test_fastapi.py
├── test_iterative_matrix_builder.py
├── test_zone_aware.py
└── test_integration.py
```

---

## Verification Steps

### 1. Check for Import Errors
```bash
# After moving each file group, verify no import errors:
python -c "import webrotas.domain.routing.processor"
python -c "import webrotas.infrastructure.routing.osrm"
python -c "import webrotas.utils.converters.geojson"
```

### 2. Run Tests
```bash
# Run tests after each phase to catch broken imports early:
uv run pytest tests/ -v
```

### 3. Check for Circular Imports
```bash
# Use Python's import checker:
python -m py_compile src/webrotas/**/*.py
```

### 4. Lint and Type Check
```bash
# If using ruff or similar:
ruff check src/webrotas/
# If using mypy:
mypy src/webrotas/
```

---

## Rollback Plan

If issues arise during migration:

1. **Keep old files during transition**
   - Don't delete old `api_routing.py`, etc. until new structure is verified
   - Create compatibility shims in old locations pointing to new locations

2. **Compatibility shims example**
   ```python
   # Old api_routing.py (now a compatibility shim)
   from webrotas.infrastructure.routing.osrm import OSRMClient
   from webrotas.domain.avoid_zones.processor import process_avoidzones
   
   # Re-export for backward compatibility (temporary)
   __all__ = ["OSRMClient", "process_avoidzones"]
   ```

3. **Git branch strategy**
   - Work in a feature branch: `refactor/reorganize-codebase`
   - Small commits for each phase
   - Test thoroughly before merging

---

## Performance Considerations

- **No runtime performance impact**: Python imports are executed once at startup
- **Slightly faster startup**: Smaller modules load faster (once you delete old files)
- **Better caching**: Smaller modules = better Python import caching

---

## Post-Refactoring Tasks

1. Update `WARP.md` with new directory structure
2. Update any internal documentation references
3. Configure linter to enforce layer boundaries:
   - Domain shouldn't import infrastructure
   - Infrastructure shouldn't import API layer
4. Consider adding a `conftest.py` for shared test fixtures
5. Update CI/CD if it has module-specific linting rules
