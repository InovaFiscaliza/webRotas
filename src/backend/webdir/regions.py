#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
regions.py

Este módulo fornece funções utilitárias para operações com regiões geográficas representadas
por bounding boxes. As funções permitem verificar se uma região está contida dentro de outra
e extrair a bounding box de uma região específica a partir de uma lista de descrições.

Funções incluídas:
- is_region_inside_another: Verifica se uma região está completamente dentro de outra.
- extrair_bounding_box_de_regioes: Extrai a bounding box de uma região nomeada.

Formato esperado para as regiões:
Cada região deve ser um dicionário com ao menos as chaves:
- 'name': identificador da região (ex: 'boundingBoxRegion')
- 'coord': lista de coordenadas geográficas em formato [ [lat, lon], ... ]
"""

def is_region_inside_another(inner_region: list, outer_region: list) -> bool:
    """
    Checks whether the 'boundingBoxRegion' in `inner_region` is completely inside the
    'boundingBoxRegion' in `outer_region`.

    :param inner_region: List containing a region dict with key 'name' == 'boundingBoxRegion'.
    :param outer_region: List containing a region dict with key 'name' == 'boundingBoxRegion'.
    :return: True if inner_region is fully inside outer_region, False otherwise.
    """
    inner_bbox = extrair_bounding_box_de_regioes(inner_region)
    outer_bbox = extrair_bounding_box_de_regioes(outer_region)

    if not inner_bbox or not outer_bbox:
        return False

    lon_min_i, lat_min_i, lon_max_i, lat_max_i = inner_bbox
    lon_min_o, lat_min_o, lon_max_o, lat_max_o = outer_bbox

    return (
        lon_min_o <= lon_min_i and
        lat_min_o <= lat_min_i and
        lon_max_i <= lon_max_o and
        lat_max_i <= lat_max_o
    )
    
def extrair_bounding_box_de_regioes(regioes: list, nome_alvo: str = "boundingBoxRegion") -> tuple:
    """
    Extrai o bounding box de uma região nomeada dentro de uma lista de regiões.

    :param regioes: Lista de dicionários contendo as regiões, onde cada item tem chave 'nome' e 'coord'.
    :param nome_alvo: Nome da região alvo para extração do bounding box.
    :return: Tupla no formato (lon_min, lat_min, lon_max, lat_max), ou None se não encontrada.
    """
    for regiao in regioes:
        if regiao.get("name", "") == nome_alvo:
            coords = regiao.get("coord", [])
            if len(coords) >= 3:
                lon_min = coords[0][1]
                lat_min = coords[2][0]
                lon_max = coords[1][1]
                lat_max = coords[0][0]
                return (lon_min, lat_min, lon_max, lat_max)
    return None        