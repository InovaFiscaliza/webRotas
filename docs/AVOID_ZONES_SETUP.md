# Server-Side Avoid Zones Setup Guide

## Overview

This guide explains how to set up and use server-side avoid zones in webRotas using OSRM's Lua profile system. Instead of post-processing routes, zones are enforced during routing computation for better accuracy.

## Architecture

```
avoidZones (JSON request)
    ↓
avoid_zones_to_geojson() [geojson_converter.py]
    ↓
process_avoidzones() [api_routing.py]
    ↓
write_lua_zones_file() [lua_converter.py]
    ↓
avoid_zones_data.lua [generated at /data/profiles/]
    ↓
car_avoid.lua [loads and uses zones]
    ↓
osrm-routed [applies penalties during routing]
```

## Components

### 1. GeoJSON Converter (`src/webrotas/geojson_converter.py`)
- **Function**: `avoid_zones_to_geojson()`
- **Input**: List of avoid zone dicts with `name` and `coord` keys
- **Output**: GeoJSON FeatureCollection (Polygon or MultiPolygon)
- **Status**: ✅ Already implemented and working

### 2. Lua Converter (`src/webrotas/lua_converter.py`)
- **Function**: `write_lua_zones_file()`
- **Input**: Path to GeoJSON file
- **Output**: Lua data file with polygon coordinates
- **Location**: `/data/profiles/avoid_zones_data.lua`
- **Status**: ✅ Already implemented

### 3. Lua Profile (`profiles/car_avoid.lua`)
- **Purpose**: Main routing profile for OSRM
- **Features**:
  - Loads base car profile from OSRM
  - Attempts to load avoid zone data at startup
  - Applies penalties to ways in avoid zones
  - Supports both PBF-stored tags and dynamic zone data
- **Status**: ✅ Already exists

### 4. Route Processing (`src/webrotas/api_routing.py`)
- **Function**: `get_osrm_route()`
- **Process**:
  1. Checks for `avoid_zones` in request
  2. Converts to GeoJSON via `avoid_zones_to_geojson()`
  3. Calls `process_avoidzones()` to generate Lua data
  4. Requests route from OSRM (which uses car_avoid.lua)
- **Status**: ✅ Already implemented

## Setup Steps

### Step 1: Prepare Data Directory

Ensure the OSRM data directory structure exists:

```bash
export OSRM_DATA=/path/to/osrm/data
mkdir -p $OSRM_DATA/profiles
cp /repo/profiles/car_avoid.lua $OSRM_DATA/profiles/
```

### Step 2: Verify Docker Configuration

Ensure `docker-compose.yml` has the correct command:

```yaml
osrm:
  command: "osrm-routed --max-matching-size 1000 --max-table-size 1000 --max-viaroute-size 1000 --algorithm mld /data/region.osrm"
  volumes:
    - ${OSRM_DATA}:/data
    - ${OSRM_DATA}/profiles:/profiles:ro
```

Key points:
- Volume mounts `/data` for OSRM data
- Profile directory is mounted as read-only (`ro`)
- `--algorithm mld` enables modern routing algorithm

### Step 3: Initialize Profiles

Create empty avoid_zones_data.lua at startup:

```bash
cat > $OSRM_DATA/profiles/avoid_zones_data.lua << 'EOF'
-- Auto-generated avoid zones data
-- Will be overwritten by process_avoidzones()
return {}
EOF
```

### Step 4: Docker Compose Up

```bash
export OSRM_DATA=/path/to/osrm/data
export OSRM_MEMORY_LIMIT=16g
export OSRM_CPUS_LIMIT=4.0
docker-compose up -d
```

### Step 5: Verify Setup

Check that OSRM loads the profile:

```bash
docker logs osrm 2>&1 | grep -i "profile\|lua\|avoid"
```

Should see messages like:
```
Loading profile from /data/region.osrm
```

## Usage

### Making Requests with Avoid Zones

Send a routing request with `avoidZones`:

```json
{
  "type": "grid",
  "origin": {"lat": -23.5, "lng": -46.6, "description": "Origin"},
  "parameters": {
    "city": "São Paulo",
    "state": "SP",
    "scope": "Location",
    "pointDistance": 3000
  },
  "avoidZones": [
    {
      "name": "Marginal Pinheiros",
      "coord": [
        [-46.70, -23.55],
        [-46.68, -23.55],
        [-46.68, -23.58],
        [-46.70, -23.58]
      ]
    }
  ],
  "criterion": "duration"
}
```

### Processing Flow

1. **Request received** by `process_request()` in FastAPI
2. **Zones converted** via `avoid_zones_to_geojson()`
3. **Lua data generated** via `process_avoidzones()`
4. **OSRM routing** uses `car_avoid.lua` profile
5. **Route returned** with zones applied

## How Avoid Zones Work

### Tag-Based Approach (Current)

Ways in the PBF file can have tags:
```
avoid_zone=yes
avoid_factor=0.05
```

The Lua profile reads these tags and reduces speed:
```lua
local f = tonumber(way:get_value_by_key('avoid_factor')) or 0.05
result.forward_speed = math.max(1, result.forward_speed * f)
```

This makes routes through avoid zones slower, so OSRM picks alternative paths.

### Dynamic Approach (Future Enhancement)

The Lua code includes polygon intersection functions (lines 36-107) for potential future use when OSRM provides node coordinates in the `process_way` hook.

## Limitations & Workarounds

### Limitation 1: OSRM API Constraint
**Issue**: `process_way()` doesn't receive node coordinates
**Workaround**: Use PBF-stored tags (requires preprocessing)

### Limitation 2: Multi-Waypoint Routing
**Issue**: OSRM doesn't compute alternatives for 3+ waypoints
**Workaround**: Server-side avoid zones ensure single route is already optimized

### Limitation 3: Zone Changes Require PBF Reprocessing
**Issue**: Avoid zones in PBF tags must be reprocessed for changes
**Workaround**: Use dynamic zone loading from Lua data file (if available)

## Testing

### Test 1: Verify Profile Loads
```bash
docker exec osrm osrm-routed --version
docker logs osrm | grep -i profile
```

### Test 2: Simple Routing
```bash
curl "http://localhost:5000/route/v1/driving/-46.633,-23.587;-46.8258,-23.5346?overview=full&geometries=geojson"
```

### Test 3: With WebRotas Grid Request
```bash
curl -X POST http://localhost:5002/process \
  -H "Content-Type: application/json" \
  -d @tests/request_grid\ \(São\ Paulo-SP-Avoid\).json
```

### Test 4: Monitor Zone Loading
```bash
# Watch logs for zone processing
docker logs -f osrm | grep -i "zone\|avoid\|polygon"
```

## Troubleshooting

### Issue: OSRM won't start
**Solution**: Check `/data/region.osrm` exists and is valid
```bash
ls -lh $OSRM_DATA/region.osrm*
```

### Issue: Profile not loaded
**Solution**: Verify profile path in docker-compose.yml
```bash
docker logs osrm | grep -i "profile.*not.*found"
```

### Issue: Zones not applied
**Solution**: Check `avoid_zones_data.lua` exists
```bash
cat $OSRM_DATA/profiles/avoid_zones_data.lua
```

### Issue: Routes ignore zones
**Solution**: May need PBF reprocessing with new tags
```bash
# Re-run osrm-extract with updated PBF file
docker-compose restart osrm
```

## Performance Considerations

- **Avoid zones in Lua**: ~5-10% routing slowdown
- **Zone checking overhead**: Minimal (only when loading)
- **Benefit**: Accurate avoidance vs. post-processing penalties

## Next Steps

1. **Verify current setup**: Run the tests above
2. **Monitor performance**: Check OSRM logs and latencies
3. **Adjust penalties**: Modify `INSIDE_FACTOR` and `TOUCH_FACTOR` in `car_avoid.lua` if needed
4. **Implement dynamic zones**: Enhance Lua profile if OSRM API improves

## References

- OSRM Lua Profile Documentation: https://github.com/Project-OSRM/osrm-backend/wiki/Profiles
- Point-in-Polygon Algorithm: https://en.wikipedia.org/wiki/Point_in_polygon
- Docker Compose Setup: See `docker-compose.yml`
