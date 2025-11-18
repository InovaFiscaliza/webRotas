"""Backwards compatibility shim - imports moved to infrastructure/geospatial/shapefiles.py"""

from webrotas.infrastructure.geospatial.shapefiles import (
    GetBoundMunicipio,
    FiltrarComunidadesBoundingBox,
    FiltrarAreasUrbanizadasPorMunicipio,
    ObterMunicipiosNoBoundingBox,
    ensure_shapefile_exists,
    ensure_all_shapefiles,
)

__all__ = [
    "GetBoundMunicipio",
    "FiltrarComunidadesBoundingBox",
    "FiltrarAreasUrbanizadasPorMunicipio",
    "ObterMunicipiosNoBoundingBox",
    "ensure_shapefile_exists",
    "ensure_all_shapefiles",
]
