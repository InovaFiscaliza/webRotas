from decimal import Decimal, ROUND_HALF_UP
 
################################################################################
# Classe de cache com coordenadas normalizadas
class RouteCache:
    def __init__(self, precision=6): # Rotas com precisão de 11 cm
        self.cache = {}  # Agora será um dict de dicts: {user_id: {rota: valor}}
        self.precision = precision

    def _normalize(self, lat, lon):
        q = Decimal('1.' + '0' * self.precision)
        lat = float(Decimal(str(lat)).quantize(q, rounding=ROUND_HALF_UP))
        lon = float(Decimal(str(lon)).quantize(q, rounding=ROUND_HALF_UP))
        return lat, lon

    def _make_key(self, start_lat, start_lon, end_lat, end_lon):
        return (self._normalize(start_lat, start_lon), self._normalize(end_lat, end_lon))

    def get(self, user_id, start_lat, start_lon, end_lat, end_lon):
        key = self._make_key(start_lat, start_lon, end_lat, end_lon)
        return self.cache.get(user_id, {}).get(key)

    def set(self, user_id, start_lat, start_lon, end_lat, end_lon, value):
        key = self._make_key(start_lat, start_lon, end_lat, end_lon)
        if user_id not in self.cache:
            self.cache[user_id] = {}
        self.cache[user_id][key] = value

    def clear_user(self, user_id):
        """Limpa o cache de um usuário específico"""
        if user_id in self.cache:
            del self.cache[user_id]

    def clear_all(self):
        """Limpa todo o cache"""
        self.cache.clear()
        
################################################################################        