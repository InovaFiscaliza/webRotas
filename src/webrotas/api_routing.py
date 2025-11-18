"""Backwards compatibility shim - imports moved to infrastructure/routing/osrm.py"""

from webrotas.infrastructure.routing.osrm import (
    compute_bounding_box,
    calculate_optimal_route,
    process_avoidzones,
    load_spatial_index,
    check_route_intersections,
    get_osrm_matrix,
    get_geodesic_matrix,
    validate_matrix,
)

__all__ = [
    "compute_bounding_box",
    "calculate_optimal_route",
    "process_avoidzones",
    "load_spatial_index",
    "check_route_intersections",
    "get_osrm_matrix",
    "get_geodesic_matrix",
    "validate_matrix",
]
