"""
Backward compatibility module - re-exports routing functions from rotas.py
"""

from webrotas.rotas import (
    osrm_shortest,
    osrm_circle,
    osrm_grid,
    osrm_ordered,
    compute_routing_area,
    get_areas_urbanas_cache,
    get_polyline_comunities,
    UserData,
)

__all__ = [
    "osrm_shortest",
    "osrm_circle",
    "osrm_grid",
    "osrm_ordered",
    "compute_routing_area",
    "get_areas_urbanas_cache",
    "get_polyline_comunities",
    "UserData",
]
