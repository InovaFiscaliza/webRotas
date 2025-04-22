from shapely.geometry import box, Polygon
from shapely.ops import unary_union
import hashlib
import json

WINDOWS_PATH_MAP_CACHE = "%PROGRAMDATA%\ANATEL\webRotasCache"

class CacheBoundingBox:
    def __init__(self):
        self.cache = {}

    def _hash_bbox(self, bbox, exclusions):
        """Gera uma hash única para o bbox e exclusões"""
        key = {
            'bbox': bbox,
            'exclusions': [list(polygon.exterior.coords) for polygon in exclusions]
        }
        key_json = json.dumps(key, sort_keys=True)
        return hashlib.sha256(key_json.encode()).hexdigest()

    def _apply_exclusions(self, bbox_polygon, exclusions):
        """Remove áreas de exclusão da bounding box"""
        if not exclusions:
            return bbox_polygon
        return bbox_polygon.difference(unary_union(exclusions))

    def get_map_segment(self, bbox, exclusions=[]):
        """
        Retorna o mapa recortado da bounding box excluindo áreas.

        bbox: (minx, miny, maxx, maxy)
        exclusions: lista de shapely.Polygon com áreas a excluir
        """
        cache_key = self._hash_bbox(bbox, exclusions)

        if cache_key in self.cache:
            print("Cache HIT")
            return self.cache[cache_key]
        else:
            print("Cache MISS - recortando área")
            bbox_polygon = box(*bbox)
            result_polygon = self._apply_exclusions(bbox_polygon, exclusions)
            self.cache[cache_key] = result_polygon
            return result_polygon

    def clear_cache(self):
        """Limpa o cache"""
        self.cache.clear()
