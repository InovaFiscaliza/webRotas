# Why Avoid Zones Aren't Working - And How to Fix It

## The Problem

You've noticed that even though we have `car_avoid.lua` and `avoid_zones_data.lua`, **the zones are still not being avoided in routes**. This is because of a critical misunderstanding about how OSRM uses profiles.

## The Root Cause: Two-Stage Process

OSRM has TWO completely separate stages:

### Stage 1: PREPROCESSING (One-time, before routing)
- **Tool**: `osrm-extract`, `osrm-contract`, `osrm-partition`, `osrm-customize`
- **Input**: 
  - `region.osm.pbf` (OpenStreetMap data)
  - `car_avoid.lua` (routing profile)
- **Output**: `region.osrm` (preprocessed routing data)
- **What happens**: The profile is applied to the PBF file, determining which roads to include and what penalties to apply
- **Profile is "baked in"**: The final `region.osrm` file contains all the profile logic permanently

### Stage 2: ROUTING (Runtime, what osrm-routed does)
- **Tool**: `osrm-routed`
- **Input**: `region.osrm` (already preprocessed, profile already applied)
- **Output**: Routes
- **Profile ignored**: `osrm-routed` does NOT read the profile again
- **Why**: The profile logic is already in the preprocessed data

## Your Current Situation

```
Your Setup:
├── region.osm.pbf (OSM data)
├── profiles/car_avoid.lua (NOT USED - not applied to PBF)
├── profiles/avoid_zones_data.lua (NOT USED - not referenced during preprocess)
└── /data/region.osrm (preprocessed WITH DEFAULT CAR PROFILE)
    └── osrm-routed loads this and routes

Result: Default car profile is used
        car_avoid.lua is ignored
        Zones are not avoided
```

## The Solution: Reprocess the PBF File

To actually use `car_avoid.lua`, you must:

1. **Find your OSM PBF file**:
   ```bash
   find $OSRM_DATA -name "*.osm.pbf" -o -name "*.pbf"
   ```
   Typically: `$OSRM_DATA/region.osm.pbf`

2. **Run preprocessing with car_avoid.lua profile**:
   ```bash
   # Navigate to data directory
   cd $OSRM_DATA
   
   # Run all preprocessing steps
   osrm-extract -p /path/to/profiles/car_avoid.lua region.osm.pbf
   osrm-contract region.osrm
   osrm-partition region.osrm
   osrm-customize region.osrm
   ```

3. **This creates new routing data**:
   - `region.osrm` (with car_avoid.lua baked in)
   - `region.osrm.edge_penalties`
   - `region.osrm.partition`
   - `region.osrm.cells`
   - `region.osrm.mldgr`

4. **Restart osrm-routed**:
   ```bash
   docker-compose restart osrm
   ```

5. **Test with avoid zones**:
   Routes should now avoid the zones!

## Automated Solution: Docker-based Preprocessing

Instead of manual commands, create a preprocessing script:

```bash
#!/bin/bash
# preprocess-osrm.sh

set -e

OSRM_DATA=${OSRM_DATA:-/data}
PBF_FILE="$OSRM_DATA/region.osm.pbf"
PROFILE="$OSRM_DATA/profiles/car_avoid.lua"

if [ ! -f "$PBF_FILE" ]; then
  echo "Error: PBF file not found: $PBF_FILE"
  exit 1
fi

if [ ! -f "$PROFILE" ]; then
  echo "Error: Profile not found: $PROFILE"
  exit 1
fi

echo "Preprocessing OSM PBF with car_avoid.lua profile..."
echo "PBF: $PBF_FILE"
echo "Profile: $PROFILE"

cd "$OSRM_DATA"

echo "Step 1: Extract..."
osrm-extract -p "$PROFILE" "$PBF_FILE"

echo "Step 2: Contract..."
osrm-contract region.osrm

echo "Step 3: Partition..."
osrm-partition region.osrm

echo "Step 4: Customize..."
osrm-customize region.osrm

echo "✅ Preprocessing complete!"
echo "Created: region.osrm (with car_avoid.lua profile baked in)"
```

## Why Wasn't This Working Before?

The documentation incorrectly suggested that:
1. ❌ The profile would be loaded at runtime by osrm-routed
2. ❌ `avoid_zones_data.lua` would be dynamically loaded
3. ❌ Changing zones wouldn't require reprocessing

**Reality:**
1. ✅ Profile must be applied during preprocessing (osrm-extract)
2. ✅ Zone penalties are "baked into" the routing data
3. ✅ Changing zones DOES require reprocessing the PBF

## The Correct Workflow

```
1. Update avoidZones in test request
    ↓
2. process_avoidzones() generates avoid_zones_data.lua
    ↓
3. Update car_avoid.lua to reference new zones
    ↓
4. Reprocess PBF with osrm-extract -p car_avoid.lua
    ↓
5. Restart osrm-routed
    ↓
6. New routes avoid zones!
```

## Alternative: Client-Side Only (Current Limitation)

Since reprocessing requires the PBF file and preprocessing tools, if you don't have those available, you're limited to client-side zone handling:

- ✅ Zones are converted to GeoJSON
- ✅ Zones are analyzed for route intersections
- ✅ Penalty scores are calculated
- ❌ **Problem**: Can't choose alternatives for multi-waypoint routes (OSRM limitation)
- ❌ Result: Single route returned, no alternative to choose

## Files That Need Attention

| File | Status | What it does |
|------|--------|-------------|
| `car_avoid.lua` | ✅ Ready | Lua profile with zone logic |
| `avoid_zones_data.lua` | ✅ Generated | Zone data (currently unused at runtime) |
| `region.osm.pbf` | ❓ Unknown | Need to locate this |
| `region.osrm` | ❌ **PROBLEM** | Preprocessed without car_avoid.lua |

## To Actually Enable Zone Avoidance

### Prerequisites
1. Locate `region.osm.pbf` (your OSM data file)
2. Ensure OSRM preprocessing tools are available (in container or system)
3. Have disk space for preprocessing

### Steps
1. Ensure `car_avoid.lua` exists in profiles directory
2. Ensure `avoid_zones_data.lua` is generated (happens on request)
3. Run preprocessing with car_avoid.lua:
   ```bash
   osrm-extract -p $OSRM_DATA/profiles/car_avoid.lua $OSRM_DATA/region.osm.pbf
   osrm-contract $OSRM_DATA/region.osrm
   osrm-partition $OSRM_DATA/region.osrm
   osrm-customize $OSRM_DATA/region.osrm
   ```
4. Restart OSRM container
5. Test routes - zones should now be avoided

## Summary

**Why zones didn't work**: The profile wasn't applied during preprocessing

**How to fix it**: Reprocess the PBF file with the car_avoid.lua profile

**Timeline**: One-time setup (takes 5-30 minutes depending on PBF size)

**Result**: Permanent zone avoidance in all routes

---

This explains the gap between the documentation and reality. The infrastructure is correct; it just requires preprocessing the data properly.
