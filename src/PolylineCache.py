#!/usr/bin/env python3
"""
    Classe PolylineCache

    Implementa um cache de polylines agrupadas por regiões geográficas, identificadas por hash.

    Funcionalidade:
        - Armazenar, recuperar, limpar e contar polylines por região (hash de coordenadas).
"""

import hashlib
import json

class PolylineCache:
    def __init__(self):
        # Armazena {hash_da_regiao: [lista de polylines]}
        self.cache = {}

    def __contains__(self, chave):
        return chave in self.cache

    @staticmethod
    def from_dict(data):
        obj = PolylineCache()
        if isinstance(data, dict):
            obj.cache = data
        return obj

    def _hash_bbox(self, regioes, tamanho=12):
        """Gera hash determinístico da lista de regiões"""
        regioes_json = json.dumps(regioes, sort_keys=True)
        hash_obj = hashlib.sha256(regioes_json.encode('utf-8'))
        return hash_obj.hexdigest()[:tamanho]

    def add_polyline(self, regioes, polyline):
        """Adiciona uma polyline ao cache da região"""
        chave = self._hash_bbox(regioes)
        if chave not in self.cache:
            self.cache[chave] = {}
        self.cache[chave]['polyline'] = polyline

    def get_polylines(self, regioes):
        """Retorna lista de polylines da região"""
        chave = self._hash_bbox(regioes)
        ret = self.cache.get(chave, {}).get('polyline')
        if ret is None:
            ret = []
        return ret

    def clear_regiao(self, regioes):
        """Remove todas as polylines de uma região"""
        chave = self._hash_bbox(regioes)
        if chave in self.cache:
            del self.cache[chave]

    def get_by_key(self, chave):
        """Retorna lista de polylines diretamente pela chave"""
        ret = self.cache.get(chave, {}).get('polyline')
        if ret is None:
            ret = []
        return ret

    def clear_regioes_pela_chave(self, chave):
        """Remove todas as polylines da chave diretamente"""
        if chave in self.cache:
            del self.cache[chave]

    def clear_all(self):
        """Limpa todo o cache"""
        self.cache.clear()

    def count_polylines(self, regioes):
        """Retorna número de polylines da região"""
        chave = self._hash_bbox(regioes)
        return len(self.cache.get(chave, []))
