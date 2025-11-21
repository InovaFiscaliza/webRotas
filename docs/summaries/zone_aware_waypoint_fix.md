# Zone-Aware Routing Waypoint Fix

## Problem

The `generate_boundary_waypoints()` function in `src/webrotas/domain/routing/zone_aware.py` was generating intermediate waypoints by offsetting from the **center** of the avoid zone's bounding box. This created a critical flaw:

- When offsetting from the center of the bounding box, waypoints could still be inside the avoid zone
- The offset distance (1-10 km) might not be sufficient to escape a large zone when starting from its center
- Routes through these waypoints could still pass through or near the avoid zones they were meant to bypass

**Example:** A zone with bounds [lat: -23.6 to -23.5, lng: -46.6 to -46.5]:
- Center is at (-23.55, -46.55)
- Offset of 1km north from center → lat -23.4591 (still close to zone)
- **Risk:** Waypoint might still be inside or barely outside the zone boundary

## Solution

Changed waypoint generation to offset from the **edges** of the bounding box, not the center:

### Key Changes

1. **Edge-based waypoints**: Each cardinal direction (N, S, E, W) now offsets from its respective edge:
   - North: offset from `maxlat` (top edge)
   - South: offset from `minlat` (bottom edge)
   - East: offset from `maxlng` (right edge)
   - West: offset from `minlng` (left edge)

2. **Additional corner waypoints**: Added 4 corner waypoints for better coverage of complex zones:
   - Northeast, Northwest, Southeast, Southwest
   - Useful for routing around large or irregularly-shaped zones

3. **Total waypoints**: 8 waypoints per zone (4 edges + 4 corners) instead of 4

### Coordinate Calculation

**Old approach:**
```python
center_lat = (minlat + maxlat) / 2
center_lng = (minlng + maxlng) / 2
offset_lat, offset_lng = _offset_point(center_lat, center_lng, direction, offset_km)
```

**New approach:**
```python
# North waypoint: offset outward from top edge
north_waypoint = (maxlat + offset_deg_lat, (minlng + maxlng) / 2)

# South waypoint: offset outward from bottom edge
south_waypoint = (minlat - offset_deg_lat, (minlng + maxlng) / 2)

# East waypoint: offset outward from right edge
east_waypoint = ((minlat + maxlat) / 2, maxlng + offset_deg_lng)

# West waypoint: offset outward from left edge
west_waypoint = ((minlat + maxlat) / 2, minlng - offset_deg_lng)

# Corner waypoints for better zone coverage
northeast = (maxlat + offset_deg_lat, maxlng + offset_deg_lng)
northwest = (maxlat + offset_deg_lat, minlng - offset_deg_lng)
southeast = (minlat - offset_deg_lat, maxlng + offset_deg_lng)
southwest = (minlat - offset_deg_lat, minlng - offset_deg_lng)
```

## Benefits

1. **Guaranteed exterior waypoints**: All waypoints are positioned outside the bounding box by construction
2. **Better zone avoidance**: Routes through these waypoints have much higher probability of avoiding zones
3. **Improved coverage**: 8 waypoints instead of 4 means better chance of finding viable routes around zones
4. **Consistent logic**: Waypoint offset is always away from the zone (positive direction)

## Verification

Test shows all 8 waypoints correctly positioned outside a test zone:
- Polygon bounds: lng [-46.6, -46.5], lat [-23.6, -23.5]
- 1km offset applied

```
✓ north     : lat=-23.4910, lng=-46.5500  (outside, north of maxlat)
✓ south     : lat=-23.6090, lng=-46.5500  (outside, south of minlat)
✓ east      : lat=-23.5500, lng=-46.4902  (outside, east of maxlng)
✓ west      : lat=-23.5500, lng=-46.6098  (outside, west of minlng)
✓ northeast : lat=-23.4910, lng=-46.4902  (corner)
✓ northwest : lat=-23.4910, lng=-46.6098  (corner)
✓ southeast : lat=-23.6090, lng=-46.4902  (corner)
✓ southwest : lat=-23.6090, lng=-46.6098  (corner)
```

## Files Modified

- `src/webrotas/domain/routing/zone_aware.py`:
  - Refactored `generate_boundary_waypoints()` function
  - Changed from center-based offsets to edge-based offsets
  - Added corner waypoints for improved zone coverage
  - Improved logging to show waypoint generation details

## Impact on Routing

When the router encounters multiple avoid zones:
1. Generates 8 exterior waypoints for each zone at progressive distances (1.5km, 3km, 5km, 7.5km, 10km)
2. Tries single waypoints first, then pairs
3. Returns the shortest viable route that avoids the zones
4. Much better success rate due to waypoints being reliably exterior to zones
