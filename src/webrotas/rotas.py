"""Backwards compatibility shim - imports moved to domain/routing/processor.py"""

from webrotas.domain.routing.processor import (
    RouteProcessor,
    UserData,
    compute_routing_area,
    get_areas_urbanas_cache,
    get_polyline_comunities,
)

__all__ = [
    "RouteProcessor",
    "UserData",
    "compute_routing_area",
    "get_areas_urbanas_cache",
    "get_polyline_comunities",
]
