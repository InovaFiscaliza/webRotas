#!/usr/bin/env python3

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
 
################################################################################
# Classe de cache de rotas ponto a ponto com coordenadas normalizadas
class RouteCache:
    def __init__(self, precision=6): # Rotas com precisão de 11 cm
        self.cache = {}  # Agora será um dict de dicts: {user_id: {rota: valor}}
        self.precision = precision

    def _hash_bbox(self, regioes, tamanho=12):
        regioes_json = json.dumps(regioes, sort_keys=True)
        hash_obj = hashlib.sha256(regioes_json.encode('utf-8'))
        hash_completo = hash_obj.hexdigest()
        return hash_completo[:tamanho]
    
    def _normalize(self, lat, lon):
        q = Decimal('1.' + '0' * self.precision)
        lat = float(Decimal(str(lat)).quantize(q, rounding=ROUND_HALF_UP))
        lon = float(Decimal(str(lon)).quantize(q, rounding=ROUND_HALF_UP))
        return lat, lon

    def _make_key(self, start_lat, start_lon, end_lat, end_lon):
        return (self._normalize(start_lat, start_lon), self._normalize(end_lat, end_lon))

    def get(self, regioes, start_lat, start_lon, end_lat, end_lon):
        chave = self._hash_bbox(regioes)
        key = self._make_key(start_lat, start_lon, end_lat, end_lon)
        return self.cache.get(chave, {}).get(key)

    def set(self, regioes, start_lat, start_lon, end_lat, end_lon, value):
        chave = self._hash_bbox(regioes)
        key = self._make_key(start_lat, start_lon, end_lat, end_lon)
        if chave not in self.cache:
            self.cache[chave] = {}
        self.cache[chave][key] = value

    def clear_regioes(self, regioes):
        """Limpa o cache de uma regiao específica"""
        chave = self._hash_bbox(regioes)
        if chave in self.cache:
            del self.cache[chave]
    
    def clear_regioes_pela_chave(self, chave):
        """Limpa o cache de uma regiao específica"""
        if chave in self.cache:
            del self.cache[chave]        

    def clear_all(self):
        """Limpa todo o cache"""
        self.cache.clear()
        
################################################################################        