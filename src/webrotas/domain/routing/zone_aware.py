"""
Zone-aware routing with dynamic waypoint insertion.

When segment-based alternatives all cross avoid zones, this module:
1. Identifies the zone blocking the route
2. Generates candidate waypoints around the zone boundary
3. Routes through different waypoints to find viable paths
4. Returns routes that avoid the zones
"""

import math
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass

from webrotas.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class BoundaryPoint:
    """A point on or near a zone boundary."""

    lat: float
    lng: float
    direction: str  # "north", "south", "east", "west", "corner"
    zone_index: int


def _get_polygon_bounds(polygon) -> Tuple[float, float, float, float]:
    """Get bounding box (minlng, minlat, maxlng, maxlat)."""
    bounds = polygon.bounds
    return bounds[0], bounds[1], bounds[2], bounds[3]


def _offset_point(
    lat: float, lng: float, direction: str, offset_km: float = 1.0
) -> Tuple[float, float]:
    """
    Offset a point in a given direction.

    Args:
        lat: Latitude
        lng: Longitude
        direction: "north", "south", "east", "west"
        offset_km: Distance in kilometers

    Returns:
        (new_lat, new_lng)
    """
    # Approximate: 1 degree = 111 km
    lat_offset = offset_km / 111.0
    lng_offset = offset_km / (111.0 * math.cos(math.radians(lat)))

    if direction == "north":
        return lat + lat_offset, lng
    elif direction == "south":
        return lat - lat_offset, lng
    elif direction == "east":
        return lat, lng + lng_offset
    elif direction == "west":
        return lat, lng - lng_offset
    else:
        return lat, lng


def generate_boundary_waypoints(
    polygons: List, avoid_zones_list: List[Dict[str, Any]], offset_km: float = 1.0
) -> List[BoundaryPoint]:
    """
    Generate waypoints around zone boundaries for routing around obstacles.

    Waypoints are placed OUTSIDE the bounding box at a safe distance from the zone.
    Each direction offset is calculated from the respective edge of the bounding box,
    not from the center, to ensure waypoints are always exterior to the zone.

    Args:
        polygons: List of shapely polygon objects
        avoid_zones_list: Original avoid_zones list with metadata
        offset_km: Offset distance in km from zone boundary (positive = away from zone)

    Returns:
        List of BoundaryPoint objects
    """
    boundary_points = []

    for zone_idx, (polygon, zone_data) in enumerate(zip(polygons, avoid_zones_list)):
        try:
            minlng, minlat, maxlng, maxlat = _get_polygon_bounds(polygon)

            # Calculate offsets from the edges of the bounding box, not the center
            # This ensures waypoints are outside the zone boundary
            offset_deg_lat = offset_km / 111.0
            # Use midpoint latitude for longitude offset calculation
            mid_lat = (minlat + maxlat) / 2
            offset_deg_lng = offset_km / (111.0 * math.cos(math.radians(mid_lat)))

            # Generate waypoints from the edges, offset outward
            edge_waypoints = [
                # North: offset from top edge, going north
                (maxlat + offset_deg_lat, (minlng + maxlng) / 2, "north"),
                # South: offset from bottom edge, going south
                (minlat - offset_deg_lat, (minlng + maxlng) / 2, "south"),
                # East: offset from right edge, going east
                ((minlat + maxlat) / 2, maxlng + offset_deg_lng, "east"),
                # West: offset from left edge, going west
                ((minlat + maxlat) / 2, minlng - offset_deg_lng, "west"),
            ]

            # Also add corner waypoints for complex zones
            corner_waypoints = [
                # Northeast corner
                (maxlat + offset_deg_lat, maxlng + offset_deg_lng, "northeast"),
                # Northwest corner
                (maxlat + offset_deg_lat, minlng - offset_deg_lng, "northwest"),
                # Southeast corner
                (minlat - offset_deg_lat, maxlng + offset_deg_lng, "southeast"),
                # Southwest corner
                (minlat - offset_deg_lat, minlng - offset_deg_lng, "southwest"),
            ]

            # Combine edge and corner waypoints
            all_waypoints = edge_waypoints + corner_waypoints

            for lat, lng, direction in all_waypoints:
                boundary_points.append(
                    BoundaryPoint(
                        lat=lat, lng=lng, direction=direction, zone_index=zone_idx
                    )
                )

            logger.info(
                f"Generated {len(all_waypoints)} boundary waypoints for zone '{zone_data.get('name', f'Zone {zone_idx}')}' "
                f"at {offset_km}km offset from edges (min: {minlat:.4f},{minlng:.4f}, max: {maxlat:.4f},{maxlng:.4f})"
            )
        except Exception as e:
            logger.error(f"Error generating boundary points for zone {zone_idx}: {e}")
            continue

    return boundary_points


async def try_route_with_intermediate_waypoints(
    start_coord: Dict[str, float],
    end_coord: Dict[str, float],
    intermediate_coords: List[Dict[str, float]],
    request_osrm_fn,
) -> Dict[str, Any]:
    """
    Request a route through intermediate waypoints.

    Args:
        start_coord: Starting coordinate
        end_coord: Ending coordinate
        intermediate_coords: List of intermediate waypoints to try
        request_osrm_fn: Async function to call OSRM

    Returns:
        Dict with route data or empty dict if failed
    """
    try:
        # Build coordinate string: start -> intermediate(s) -> end
        coords_list = [start_coord] + intermediate_coords + [end_coord]
        coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in coords_list])

        params = {
            "alternatives": 1,
            "overview": "full",
            "geometries": "geojson",
        }

        logger.info(
            f"Trying route with {len(intermediate_coords)} intermediate waypoint(s)"
        )

        osrm_response = await request_osrm_fn(
            request_type="route",
            coordinates=coord_str,
            params=params,
        )

        if osrm_response.get("routes"):
            route = osrm_response["routes"][0]
            return {
                "geometry": route.get("geometry", {}).get("coordinates", []),
                "distance": route.get("distance", 0),
                "duration": route.get("duration", 0),
                "intermediate_waypoints": len(intermediate_coords),
                "success": True,
            }

        return {"success": False}

    except Exception as e:
        logger.warning(f"Route with intermediate waypoints failed: {e}")
        return {"success": False}


async def find_route_around_zones(
    start_coord: Dict[str, float],
    waypoints: List[Dict[str, float]],
    request_osrm_fn,
    polygons: List,
    avoid_zones_list: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Try to find a route that avoids zones by inserting intermediate waypoints.

    Strategy:
    1. Generate boundary waypoints at progressive distances (1.5km, 3km, 5km)
    2. Try routes through each boundary waypoint
    3. Select the shortest route that avoids zones

    Args:
        start_coord: Starting coordinate
        waypoints: List of waypoints to visit
        request_osrm_fn: Async function to call OSRM
        polygons: List of shapely polygon objects (avoid zones)
        avoid_zones_list: Original avoid_zones list

    Returns:
        Dict with complete route or None if no viable path found
    """
    try:
        # Build full waypoint list: start + all waypoints
        all_waypoints = [start_coord] + waypoints

        # Try progressive offset distances to find route around zones
        best_route = None
        best_distance = float("inf")
        offset_distances = [1.5, 3.0, 5.0, 7.5, 10.0]  # Try increasingly larger offsets

        for offset_km in offset_distances:
            boundary_points = generate_boundary_waypoints(
                polygons, avoid_zones_list, offset_km=offset_km
            )

            if not boundary_points:
                logger.debug(f"No boundary waypoints at offset {offset_km}km")
                continue

            logger.info(
                f"Trying {len(boundary_points)} boundary waypoints at {offset_km}km offset"
            )

            # Try single waypoints first
            for bp in boundary_points:
                intermediate = {"lat": bp.lat, "lng": bp.lng}
                route = await try_route_with_intermediate_waypoints(
                    all_waypoints[0],
                    all_waypoints[-1],
                    [intermediate],
                    request_osrm_fn,
                )

                if route.get("success") and route.get("distance", 0) < best_distance:
                    best_distance = route["distance"]
                    best_route = route
                    logger.info(
                        f"Found viable route with {route['distance']:.0f}m "
                        f"via {bp.direction} waypoint at {offset_km}km offset"
                    )

            # For larger zones, try pairs of waypoints to force route around zone
            if len(boundary_points) >= 2:
                logger.info(f"Trying boundary waypoint pairs at {offset_km}km offset")
                for i in range(len(boundary_points)):
                    for j in range(i + 1, len(boundary_points)):
                        bp1, bp2 = boundary_points[i], boundary_points[j]
                        intermediates = [
                            {"lat": bp1.lat, "lng": bp1.lng},
                            {"lat": bp2.lat, "lng": bp2.lng},
                        ]
                        route = await try_route_with_intermediate_waypoints(
                            all_waypoints[0],
                            all_waypoints[-1],
                            intermediates,
                            request_osrm_fn,
                        )

                        if (
                            route.get("success")
                            and route.get("distance", 0) < best_distance
                        ):
                            best_distance = route["distance"]
                            best_route = route
                            logger.info(
                                f"Found viable pair route with {route['distance']:.0f}m "
                                f"via {bp1.direction}-{bp2.direction} waypoints at {offset_km}km offset"
                            )

        if best_route:
            return best_route

        logger.warning("No viable route found around zones")
        return None

    except Exception as e:
        logger.error(f"Error finding route around zones: {e}")
        return None
