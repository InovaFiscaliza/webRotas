"""Backwards compatibility shim - imports moved to domain/routing/zone_aware.py"""

from webrotas.domain.routing.zone_aware import (
    generate_boundary_waypoints,
    find_route_around_zones,
    BoundaryPoint,
)

__all__ = ["generate_boundary_waypoints", "find_route_around_zones", "BoundaryPoint"]
