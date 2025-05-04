#!/usr/bin/env python3
"""
    Classe PolylineCache

    Implementa um sistema simples e eficiente de cache de geometrias (polylines),
    organizadas e indexadas unicamente por regiões geográficas.

    Funcionalidade principal:
        - Armazena e recupera listas de polylines associadas a uma determinada região,
          identificada por um hash SHA-256 truncado da sua representação JSON ordenada.

    Recursos disponíveis:
        - add_polyline(regioes, polyline): Adiciona uma nova polyline à região especificada.
        - get_polylines(regioes): Recupera todas as polylines associadas à região.
        - clear_regiao(regioes): Remove todas as polylines da região especificada.
        - clear_all(): Limpa completamente o cache.
        - count_polylines(regioes): Retorna o número de polylines armazenadas para uma região.

    Chave de indexação:
        - As regiões são identificadas por um hash (12 primeiros caracteres de um SHA-256),
          calculado a partir da serialização JSON ordenada da lista de coordenadas.

    Uso típico:
        - Ideal para aplicações de roteamento, visualização geográfica ou qualquer sistema
          que necessite armazenar temporariamente conjuntos de geometrias agrupadas por região,
          com acesso rápido e baixa complexidade.
"""

import hashlib
import json

class PolylineCache:
    def __init__(self):
        self.cache = {}  # {hash_da_regiao: [lista de polylines]}

    def __contains__(self, chave):
        return chave in self.cache

    def _hash_bbox(self, regioes, tamanho=12):
        regioes_json = json.dumps(regioes, sort_keys=True)
        hash_obj = hashlib.sha256(regioes_json.encode('utf-8'))
        hash_completo = hash_obj.hexdigest()
        return hash_completo[:tamanho]

    def add_polyline(self, regioes, polyline):
        """Adiciona uma polyline ao cache de uma região"""
        chave = self._hash_bbox(regioes)
        if chave not in self.cache:
            self.cache[chave] = []
        self.cache[chave] = polyline

    def get_polylines(self, regioes):
        """Retorna todas as polylines da região"""
        chave = self._hash_bbox(regioes)
        return self.cache.get(chave, [])

    def clear_regiao(self, regioes):
        """Remove todas as polylines de uma região"""
        chave = self._hash_bbox(regioes)
        if chave in self.cache:
           self.cache[chave] = []

    def get_by_key(self, chave):
        """Retorna a lista de polylines associadas à chave, ou lista vazia"""
        return self.cache.get(chave, [])

            
    def clear_regioes_pela_chave(self, chave): 
        self.cache[chave] = []  

    def clear_all(self):
        """Remove todo o cache"""
        self.cache = {}

    def count_polylines(self, regioes):
        """Conta quantas polylines há na região"""
        chave = self._hash_bbox(regioes)
        return len(self.cache.get(chave, []) )
