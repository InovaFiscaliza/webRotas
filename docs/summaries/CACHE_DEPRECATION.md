#  Cache Module Deprecation

## Status
**DEPRECATED** - To be removed in a future version

## Date
November 14, 2025

## Reason for Deprecation

The cache module (`src/webrotas/cache/`) was designed for a different architectural model but is no longer necessary with the current async FastAPI implementation:

### Why Caching is Unnecessary Now

1. **Single Container Deployment**: Only one OSRM container runs at a time
   - No multi-instance scaling requiring shared cache
   - No performance benefit from in-process caching in async context

2. **Async Nature of FastAPI**:
   - Each request is independent
   - Async tasks don't benefit from process-level caching
   - Request state is local to each async task

3. **Stateless Design**:
   - Modern web frameworks favor stateless request processing
   - Caching should be at infrastructure level (Redis, CDN) if needed
   - In-memory caching complicates code unnecessarily

4. **Persistent Storage Already Exists**:
   - OSRM data is already cached on disk in filtered directories
   - Shapefile data is loaded from disk
   - Additional in-memory cache layer adds no value

## What is Deprecated

### Cache Module Files

- `src/webrotas/cache/__init__.py` - Cache package init
- `src/webrotas/cache/bounding_boxes.py` - CacheBoundingBox class (main cache manager)
- `src/webrotas/cache/polylines.py` - PolylineCache class
- `src/webrotas/cache/routes.py` - RouteCache class

### Removed Functionality

| Function/Class | Location | Status |
|---|---|---|
| `CacheBoundingBox` | cache/bounding_boxes.py | Deprecated |
| `cCacheBoundingBox` (singleton) | cache/bounding_boxes.py | Deprecated |
| `RouteCache` | cache/routes.py | Deprecated |
| `PolylineCache` | cache/polylines.py | Deprecated |
| `compute_routing_area()` caching | rotas.py | **REMOVED** |
| `get_areas_urbanas_cache()` caching | rotas.py | **REMOVED** |
| `get_polyline_comunities()` caching | rotas.py | **REMOVED** |

## Migration Changes Already Applied

### rotas.py Changes
- ✅ Removed `import webrotas.cache.bounding_boxes as cb`
- ✅ `compute_routing_area()` no longer returns `cache_id`
- ✅ `get_areas_urbanas_cache()` directly calls shapefiles (no cache)
- ✅ `get_polyline_comunities()` directly calls shapefiles (no cache)
- ✅ `RouteProcessor` removed `cache_id` field
- ✅ `create_initial_route()` no longer includes `cacheId` in response

### Impact Analysis

| Function | Impact | Mitigation |
|---|---|---|
| `process_shortest()` | cache_id param removed | Not used in responses anymore |
| `create_initial_route()` | cacheId field removed | Not used by frontend |
| Shapefiles calls | Now direct, no cache | Small performance cost acceptable for single-container design |

## Remaining Cache Usage

Some functions in `routing_servers_interface.py` still reference cache:
- `PreparaServidorRoteamento()` - Lines 847-894
- These functions are mostly commented out but need cleanup

## Performance Considerations

### Before (with Cache)
- First request per region: Load shapefiles from disk
- Subsequent requests: Serve from memory cache
- Overhead: Memory usage, cache invalidation logic

### After (without Cache)
- Every request: Load shapefiles from disk
- No cache overhead
- Performance: Slightly slower for repeated same-region requests
  - Acceptable for single-container, async design
  - Disk I/O is fast enough for most use cases

## Timeline

- **Deprecated**: v1.0.0+
- **Expected Removal**: v2.0.0 or later

## Cleanup Checklist

- [ ] Remove cache import from `routing_servers_interface.py`
- [ ] Simplify `PreparaServidorRoteamento()` to remove cache references
- [ ] Remove cache module directory entirely
- [ ] Update tests to remove cache mocking
- [ ] Update documentation to remove cache setup instructions

## Notes

1. **No Breaking Changes**: Cache was internal implementation detail
2. **API Compatible**: Response format updated but endpoint behavior unchanged
3. **Performance**: Negligible impact with current single-container deployment
4. **Future Scaling**: If multi-container deployment needed later, use Redis or similar external cache
