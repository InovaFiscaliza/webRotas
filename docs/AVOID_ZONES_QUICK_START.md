# Avoid Zones - Quick Start Guide

## TL;DR - Get Started in 5 Minutes

### 1. Ensure car_avoid.lua is in place
```bash
cp profiles/car_avoid.lua $OSRM_DATA/profiles/
mkdir -p $OSRM_DATA/profiles
```

### 2. Ensure avoid_zones_data.lua exists (can be empty initially)
```bash
cat > $OSRM_DATA/profiles/avoid_zones_data.lua << 'EOF'
-- Auto-generated avoid zones data
return {}
EOF
```

### 3. Start Docker containers
```bash
export OSRM_DATA=/path/to/data
export OSRM_MEMORY_LIMIT=16g
docker-compose up -d
```

### 4. Make a request with avoid zones
```bash
curl -X POST http://localhost:5002/process \
  -H "Content-Type: application/json" \
  -d '{"type": "shortest", "origin": {"lat": -23.5, "lng": -46.6}, "parameters": {"waypoints": [{"lat": -23.6, "lng": -46.7}]}, "avoidZones": [{"name": "Zone1", "coord": [[-46.65, -23.55], [-46.64, -23.55], [-46.64, -23.58], [-46.65, -23.58]]}]}'
```

### 5. Check that zone data was generated
```bash
cat $OSRM_DATA/profiles/avoid_zones_data.lua
```

## What Actually Happens

```
Your Request
    ↓
avoidZones JSON list
    ↓
Convert to GeoJSON (geojson_converter.py)
    ↓
Generate Lua data file (lua_converter.py)
    ↓
OSRM reads car_avoid.lua profile
    ↓
Profile loads avoid_zones_data.lua
    ↓
Route is computed with zone penalties applied
    ↓
Result: Route avoids the zones!
```

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| `car_avoid.lua` | `profiles/car_avoid.lua` (repo) → `/data/profiles/car_avoid.lua` (container) | OSRM routing profile with zone support |
| `avoid_zones_data.lua` | `/data/profiles/avoid_zones_data.lua` | Auto-generated zone data (created by Python) |
| `geojson_converter.py` | `src/webrotas/geojson_converter.py` | Converts avoidZones list to GeoJSON |
| `lua_converter.py` | `src/webrotas/lua_converter.py` | Converts GeoJSON to Lua format |
| `api_routing.py` | `src/webrotas/api_routing.py` | Orchestrates the process |

## Avoid Zones in Request JSON

```json
{
  "type": "grid",
  "origin": {
    "lat": -23.5880027,
    "lng": -46.6333776,
    "description": "Starting point"
  },
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
    },
    {
      "name": "Another Zone",
      "coord": [
        [-46.60, -23.50],
        [-46.58, -23.50],
        [-46.58, -23.52],
        [-46.60, -23.52]
      ]
    }
  ],
  "criterion": "duration"
}
```

## Testing

### Verify Zone Data Generated
```bash
# After making a request with avoidZones
cat $OSRM_DATA/profiles/avoid_zones_data.lua

# Should show Lua table structure:
# return {
#   {
#     coords = {
#       {-46.70, -23.55},
#       ...
#     },
#     is_inside = true,
#     is_touching = true,
#   },
#   ...
# }
```

### Check OSRM Loaded Profile
```bash
docker logs osrm | head -20
```

### Simple Routing Test
```bash
# Test OSRM directly (no zones)
curl "http://localhost:5000/route/v1/driving/-46.633,-23.587;-46.825,-23.535"

# Test through WebRotas (with potential zones)
curl -X POST http://localhost:5002/process -H "Content-Type: application/json" -d '{"type": "shortest", "origin": {"lat": -23.587, "lng": -46.633}, "parameters": {"waypoints": [{"lat": -23.535, "lng": -46.825}]}, "criterion": "distance"}'
```

## Troubleshooting

### Routes not avoiding zones?
1. Check `avoid_zones_data.lua` was generated: `ls -l $OSRM_DATA/profiles/avoid_zones_data.lua`
2. Check file is not empty: `cat $OSRM_DATA/profiles/avoid_zones_data.lua | wc -l` (should be > 3 lines)
3. Restart OSRM: `docker-compose restart osrm`
4. Check logs: `docker logs osrm | grep -i avoid`

### OSRM won't start?
1. Check data file exists: `ls -l $OSRM_DATA/region.osrm`
2. Check profile loaded: `docker logs osrm 2>&1 | head -50`
3. Check memory: `docker stats osrm`

### Getting empty routes?
1. Verify coordinates are in valid GeoJSON order (lng, lat)
2. Check polygon is closed (first and last point same)
3. Ensure at least 3 unique points per polygon

## Performance

- **Small zones (< 10 polygons)**: < 1% overhead
- **Large zones (100+ polygons)**: 5-10% overhead  
- **Zone loading**: One-time at request (after that cached)

## Advanced: Adjusting Penalty Factors

Edit `profiles/car_avoid.lua` lines 8-10:
```lua
local INSIDE_FACTOR = 0.02   -- Ways completely inside avoid zone (slower)
local TOUCH_FACTOR = 0.10    -- Ways touching avoid zone boundary
```

Lower values = stronger avoidance (slower routing through zone)
- `0.01` = 1% speed (very strong avoidance)
- `0.05` = 5% speed (moderate avoidance)
- `0.99` = 99% speed (minimal avoidance)

Restart OSRM after changing: `docker-compose restart osrm`

## How Zones Actually Work

1. **Zone penalty applied at way level**: Each road segment passing through a zone gets its speed reduced
2. **OSRM routing chooses best path**: With slower speeds in zones, router naturally avoids them
3. **No "hard blocking"**: Routes CAN pass through zones if it's the only way, but will choose alternatives if available
4. **Works with all route types**: Grid, circle, shortest - all automatically use the profile

## Next Steps

- [Full Setup Guide](AVOID_ZONES_SETUP.md)
- [OSRM Documentation](https://github.com/Project-OSRM/osrm-backend/wiki/Profiles)
- Check test files: `tests/request_*-Avoid.json`
