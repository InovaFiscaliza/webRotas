"""GeoJSON conversion utilities for route data."""

from typing import Any


def avoid_zones_to_geojson(avoid_zones: list[dict]) -> dict[str, Any]:
    """Convert avoidZones list to GeoJSON FeatureCollection.
    
    Transforms a list of zone objects with coordinates into a GeoJSON FeatureCollection.
    Uses Polygon geometry if there is only one zone, otherwise uses MultiPolygon.
    
    Args:
        avoid_zones: List of zone objects, each containing:
            - name: Zone identifier/name
            - coord: List of [lng, lat] coordinate pairs forming the polygon
    
    Returns:
        GeoJSON FeatureCollection dict with appropriate geometry type:
        - Single zone: Polygon geometry in a Feature
        - Multiple zones: MultiPolygon geometry in a Feature
        
    Example:
        >>> zones = [
        ...     {
        ...         "name": "Zone1",
        ...         "coord": [[-43.1, -22.9], [-43.2, -22.9], [-43.2, -22.8], [-43.1, -22.8]]
        ...     },
        ...     {
        ...         "name": "Zone2",
        ...         "coord": [[-43.3, -22.9], [-43.4, -22.9], [-43.4, -22.8], [-43.3, -22.8]]
        ...     }
        ... ]
        >>> geojson = avoid_zones_to_geojson(zones)
        >>> geojson["type"]
        'FeatureCollection'
    """
    if not avoid_zones:
        # Return empty FeatureCollection if no zones provided
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    # Extract polygon coordinates from each zone
    polygons = []
    for zone in avoid_zones:
        coord = zone.get("coord", [])
        if coord:
            # Close the polygon if not already closed
            if coord[0] != coord[-1]:
                coord = coord + [coord[0]]
            polygons.append(coord)
    
    if not polygons:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    # Determine geometry type based on number of polygons
    if len(polygons) == 1:
        geometry = {
            "type": "Polygon",
            "coordinates": polygons[0]
        }
    else:
        geometry = {
            "type": "MultiPolygon",
            "coordinates": [[polygon] for polygon in polygons]
        }
    
    # Create a single feature with all zones
    feature = {
        "type": "Feature",
        "properties": {
            "zones_count": len(polygons),
            "zone_names": [zone.get("name", "") for zone in avoid_zones]
        },
        "geometry": geometry
    }
    
    return {
        "type": "FeatureCollection",
        "features": [feature]
    }
