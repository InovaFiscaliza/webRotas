# Deprecation Notice: RouteRequestManager

## Status
**DEPRECATED** - To be removed in a future version

## Date
November 14, 2025

## Reason for Deprecation

The `RouteRequestManager` class (in `src/webrotas/route_request_manager.py`) is no longer necessary due to architectural changes:

1. **Async Architecture**: FastAPI's async nature eliminates the need for in-process request tracking
2. **Stateless Design**: Modern web applications favor stateless request handling
3. **Simplified Code**: Logic has been integrated into `RouteProcessor` for better cohesion

## What Was Deprecated

- `RouteRequestManager` class
- Class variable `in_progress_requests` for request tracking
- Static methods `process_request()` and `find_by_route_id()`

## Replacement

All functionality has been integrated into `RouteProcessor` class:

- **`create_initial_route()`** - Generates initial route response with location details
- **`create_custom_route()`** - Generates custom route response
- **`route_for_gui()`** - Formats route data for GUI consumption
- **Route ID generation** - Handled directly in `route_service.py`

## Migration Path

### Before (using RouteRequestManager):
```python
from webrotas.route_request_manager import RouteRequestManager as rrm

current_request, new_flag = rrm.process_request(request_type, data)
processor = RouteProcessor(current_request, session_id, origin, avoid_zones, criterion)
# ... process route ...
response = current_request.create_initial_route()
```

### After (using RouteProcessor directly):
```python
from webrotas.domain.routing.processor import RouteProcessor
import uuid

route_id = str(uuid.uuid4())  # or from parameters for "ordered" type
processor = RouteProcessor(
    session_id=session_id,
    origin=origin,
    avoid_zones=avoid_zones,
    criterion=criterion,
    request_data=data,
    route_id=route_id,
)
# ... process route ...
response = processor.create_initial_route()
```

## Files Affected

- `src/webrotas/rotas.py` - Enhanced with response generation methods
- `src/webrotas/services/route_service.py` - Updated to use RouteProcessor directly
- `src/webrotas/route_request_manager.py` - **DEPRECATED**, to be removed

## Timeline

- **Deprecated**: v1.0.0+
- **Expected Removal**: v2.0.0 or later

## Notes

The cached request lookup functionality (`find_by_route_id`) is not carried forward as:
1. Async requests don't benefit from in-memory caching of request objects
2. Proper caching should be implemented at the application/database layer if needed
3. Current usage doesn't indicate this feature is actively used
