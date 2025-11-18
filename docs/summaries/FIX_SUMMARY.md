# Fix Summary: Frontend Duplicate Request Detection

## Issue
After deprecating the cache module, the frontend was treating all requests as duplicates. Only the first request would be displayed; subsequent requests were skipped.

## Root Cause
The frontend deduplication logic (Model.js) compares `cacheId` values to identify duplicate requests:
```javascript
if (initialRoute[ii].response.cacheId === routingContext[jj].response.cacheId && ...) {
    renderUpdate[ii] = false;  // Skip request
}
```

When `cacheId` was removed from the response, all responses had `cacheId = undefined`, causing the comparison `undefined === undefined` to return true, marking all requests as duplicates.

## Solution Implemented

**Added unique `cacheId` to each response:**

1. **RouteProcessor.__init__()** (Line 59):
   - Each processor instance generates a unique UUID as `cache_id`
   - This ID is NOT used for actual caching anymore
   - It's purely for frontend deduplication

2. **RouteProcessor.create_initial_route()** (Line 233):
   - Added `"cacheId": self.cache_id` to the response
   - This ensures each request response has a unique identifier

## Technical Details

### Before (Broken):
```json
{
  "routing": [{
    "response": {
      "boundingBox": [...],
      "location": {...}
    }
  }]
}
```

### After (Fixed):
```json
{
  "routing": [{
    "response": {
      "cacheId": "550e8400-e29b-41d4-a716-446655440000",
      "boundingBox": [...],
      "location": {...}
    }
  }]
}
```

## Impact

- ✅ Frontend can now properly deduplicate requests
- ✅ Each request is treated as unique (as intended)
- ✅ No frontend modifications needed
- ✅ Cache deprecation remains intact (cacheId ≠ caching)
- ✅ Minimal backend change (2 lines added)

## Files Modified

- `src/webrotas/rotas.py`
  - Line 59: Added `self.cache_id = str(uuid.uuid4())`
  - Line 233: Added `"cacheId": self.cache_id` to response

## Testing

The fix enables:
1. Multiple sequential requests to be processed correctly
2. Each request response to be unique
3. Frontend layout to update properly for each new request
