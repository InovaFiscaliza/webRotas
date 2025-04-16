from decimal import Decimal, ROUND_HALF_UP
################################################################################
# Classe de cache com coordenadas normalizadas
class RouteCache:
    def __init__(self, precision=6): # Rotas com precisão de 11 cm
        self.cache = {}
        self.precision = precision

    def _normalize(self, lat, lon):
        q = Decimal('1.' + '0' * self.precision)
        lat = float(Decimal(str(lat)).quantize(q, rounding=ROUND_HALF_UP))
        lon = float(Decimal(str(lon)).quantize(q, rounding=ROUND_HALF_UP))
        return lat, lon

    def _make_key(self, start_lat, start_lon, end_lat, end_lon):
        start = self._normalize(start_lat, start_lon)
        end = self._normalize(end_lat, end_lon)
        return (start, end)

    def get(self, start_lat, start_lon, end_lat, end_lon):
        key = self._make_key(start_lat, start_lon, end_lat, end_lon)
        return self.cache.get(key)

    def set(self, start_lat, start_lon, end_lat, end_lon, value):
        key = self._make_key(start_lat, start_lon, end_lat, end_lon)
        self.cache[key] = value
################################################################################