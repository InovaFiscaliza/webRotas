"""Backwards compatibility shim - imports moved to infrastructure/elevation/service.py"""

from webrotas.infrastructure.elevation.service import (
    enrich_waypoints_with_elevation,
)

__all__ = ["enrich_waypoints_with_elevation"]
