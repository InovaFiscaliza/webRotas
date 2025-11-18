"""Backwards compatibility shim - imports moved to domain/routing/alternatives.py"""

from webrotas.domain.routing.alternatives import (
    SegmentAlternativesBuilder,
    SegmentAlternative,
    RouteSegment,
    get_alternatives_for_multipoint_route,
)

__all__ = [
    "SegmentAlternativesBuilder",
    "SegmentAlternative",
    "RouteSegment",
    "get_alternatives_for_multipoint_route",
]
