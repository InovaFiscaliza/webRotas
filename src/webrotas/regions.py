"""Backwards compatibility shim - imports moved to domain/geospatial/regions.py"""

from webrotas.domain.geospatial.regions import (
    extrair_bounding_box_de_regioes,
    is_region_inside_another,
    compare_regions_without_bounding_box,
)

__all__ = [
    "extrair_bounding_box_de_regioes",
    "is_region_inside_another",
    "compare_regions_without_bounding_box",
]
