#!/usr/bin/env python3
"""
Este módulo fornece funções para extração e filtragem de informações geográficas de municípios brasileiros,
com base em shapefiles do IBGE e outras fontes georreferenciadas. Utiliza a biblioteca GeoPandas para
processamento espacial, e lida com áreas urbanizadas, comunidades e limites municipais.

Funcionalidades principais:

- `GetBoundMunicipio(nome_municipio, estado_sigla)`: Obtém a geometria do limite de um município e retorna
  suas coordenadas em formato de polylines.

- `FiltrarComunidadesBoundingBox(bounding_box)`: Filtra e retorna os contornos de comunidades (favelas)
  presentes dentro de um bounding box geográfico.

- `FiltrarAreasUrbanizadasPorMunicipio(municipio_nome, estado_sigla)`: Retorna as áreas urbanizadas de um
  município específico, filtrando por densidade e respeitando os limites municipais.

- `ObterMunicipiosNoBoundingBox(bounding_box)`: Lista os municípios inteiramente contidos em um bounding box.

- `ObterMunicipiosNoBoundingBoxOrdenados(bounding_box)`: Lista os municípios dentro de um bounding box,
  ordenados pela distância do centroide municipal ao centro do box.

Constantes:
- `SHAPEFILE_MUNICIPIO_PATH`: Caminho para o shapefile de municípios do Brasil (IBGE 2023).
- `SHAPEFILE_FAVELA_PATH`: Caminho para o shapefile com dados de comunidades/favelas.
- `SHAPEFILE_AREA_URBANIZADA_PATH`: Caminho para o shapefile com áreas urbanizadas do Brasil.

Dependências:
- geopandas, shapely, pyproj, e módulos locais `webRota` e `uf_code`.

Uso típico:
    from este_modulo import GetBoundMunicipio, FiltrarAreasUrbanizadasPorMunicipio, ...
    polylines = GetBoundMunicipio("Rio de Janeiro", "RJ")
"""

###########################################################################################################################
from shapely.ops import unary_union
import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon
import pyproj
import math
from pathlib import Path
import time

import uf_code as uf

# -----------------------------------------------------------------------------------#
PATH_MODULE = Path(__file__).resolve().parent
FILES = {
    "locationLimits": PATH_MODULE
    / "resources"
    / "BR_Municipios_2023.shp.parquet",  # "BR_Municipios" / "BR_Municipios_2023.shp"
    "locationUrbanAreas": PATH_MODULE
    / "resources"
    / "AU_2022_AreasUrbanizadas2019_Brasil.shp.parquet",  # "Urbanizacao" / "AU_2022_AreasUrbanizadas2019_Brasil.shp"
    "locationUrbanCommunities": PATH_MODULE
    / "resources"
    / "qg_2022_670_fcu_agregPolygon.shp.parquet",  # "Comunidades" / "qg_2022_670_fcu_agregPolygon.shp"
}
CACHE = {}


# -----------------------------------------------------------------------------------#
def read_file(type: str):
    if type not in FILES:
        raise ValueError(f'Invalid geofile type "{type}"')
    if type not in CACHE:
        CACHE[type] = gpd.read_parquet(FILES[type])
    # CACHE[type] = gpd.read_file(FILES[type])
    # CACHE[type].to_parquet(f"{FILES[type]}.parquet")
    return CACHE[type]


# -----------------------------------------------------------------------------------#
# TESTE DE PRE-CARREGAMENTO
# -----------------------------------------------------------------------------------#
for f in FILES:
    start = time.perf_counter()
    read_file(f)
    end = time.perf_counter()
    print(f"[webRotas] {f} loaded in {end - start:.2f} seconds")


# -----------------------------------------------------------------------------------#
def expand_bounding_box(box, margin_km):
    """
    Expande o bounding box em uma margem de distância ao redor (em km).

    :param box: lista com 4 pontos do bounding box no formato
                [
                    [lat_max, lon_min],
                    [lat_max, lon_max],
                    [lat_min, lon_max],
                    [lat_min, lon_min],
                ]
    :param margin_km: distância em quilômetros para expandir o bounding box
    :return: novo box expandido no mesmo formato
    """

    lat_max, lon_min = box[0]
    _, lon_max = box[1]
    lat_min, _ = box[2]

    # Calcula latitude média para ajustar longitude
    lat_mean = (lat_max + lat_min) / 2.0

    # 1 grau latitude ~ 111 km
    km_in_degree_lat = 111.0
    # 1 grau longitude ~ 111 km * cos(latitude)
    km_in_degree_lon = 111.0 * math.cos(math.radians(lat_mean))

    # Convertendo margin_km para graus
    delta_lat = margin_km / km_in_degree_lat
    delta_lon = margin_km / km_in_degree_lon if km_in_degree_lon != 0 else 0

    # Expande box
    new_box = [
        [lat_max + delta_lat, lon_min - delta_lon],
        [lat_max + delta_lat, lon_max + delta_lon],
        [lat_min - delta_lat, lon_max + delta_lon],
        [lat_min - delta_lat, lon_min - delta_lon],
    ]

    return new_box


##############################################################################################################
def uf_sigla_para_codigo_ibge(sigla):
    """
    Converte a sigla de uma Unidade Federativa (UF) brasileira para o código IBGE (CD_UF).

    Parâmetros:
        sigla (str): Sigla da UF (ex: "RJ", "SP", "DF")

    Retorna:
        int: Código IBGE correspondente (ex: 33 para RJ)
        None: Se a sigla não for reconhecida
    """
    sigla = sigla.strip().upper()

    sigla_to_ibge = {
        "RO": 11,
        "AC": 12,
        "AM": 13,
        "RR": 14,
        "PA": 15,
        "AP": 16,
        "TO": 17,
        "MA": 21,
        "PI": 22,
        "CE": 23,
        "RN": 24,
        "PB": 25,
        "PE": 26,
        "AL": 27,
        "SE": 28,
        "BA": 29,
        "MG": 31,
        "ES": 32,
        "RJ": 33,
        "SP": 35,
        "PR": 41,
        "SC": 42,
        "RS": 43,
        "MS": 50,
        "MT": 51,
        "GO": 52,
        "DF": 53,
    }

    return sigla_to_ibge.get(sigla)


##############################################################################################################
def get_bounding_box_for_municipalities(lista_municipios):
    # Carrega o shapefile dos municípios
    gdf = read_file("locationLimits")

    entrada = {
        (
            item["municipio"].strip().lower(),
            uf_sigla_para_codigo_ibge(item["siglaEstado"].strip().upper()),
        )
        for item in lista_municipios
    }

    # Filtra os municípios correspondentes
    gdf_filtrado = gdf[
        gdf.apply(
            lambda row: (
                row["NM_MUN"] is not None
                and row["CD_UF"] is not None
                and (row["NM_MUN"].strip().lower(), int(row["CD_UF"])) in entrada
            ),
            axis=1,
        )
    ]

    if gdf_filtrado.empty:
        raise ValueError("Nenhum município da lista foi encontrado no shapefile.")

    # Obtém os limites da união dos polígonos
    bounds = gdf_filtrado.total_bounds  # [minx, miny, maxx, maxy]
    minx, miny, maxx, maxy = bounds

    # Converte para o formato solicitado
    box = [
        [maxy, minx],
        [maxy, maxx],
        [miny, maxx],
        [miny, minx],
    ]
    return box


##############################################################################################################
def get_gr_data(data, gr_alvo):
    for regiao in data.get("RegioesCache", []):
        if regiao.get("GR") == gr_alvo:
            return regiao
    return None  # Se não encontrar


##############################################################################################################


def get_bounding_box_from_states(estados_siglas: list) -> list:
    """
    Retorna um bounding box que engloba todos os municípios dos estados informados,
    no formato:
        [
            [lat_max, lon_min],
            [lat_max, lon_max],
            [lat_min, lon_max],
            [lat_min, lon_min],
        ]

    :param estados_siglas (list): Lista de siglas de estados (ex: ['RJ', 'SP', 'MG'])
    :return: Lista com as 4 coordenadas do bounding box combinado
    """
    # Carrega o shapefile completo de municípios
    gdf = read_file("locationLimits")

    # Obtém os códigos dos estados a partir das siglas
    codigos_uf = [uf.SIGLAS_UF[sigla]["CD_UF"] for sigla in estados_siglas]

    # Filtra os municípios dos estados desejados
    gdf_filtrado = gdf[gdf["CD_UF"].isin(codigos_uf)]

    if gdf_filtrado.empty:
        raise ValueError(
            f"Nenhum município encontrado para os estados {estados_siglas}."
        )

    # União das geometrias
    geometria_total = unary_union(gdf_filtrado.geometry)
    minx, miny, maxx, maxy = geometria_total.bounds

    # Formato de saída: (lat, lon)
    box = [
        [maxy, minx],
        [maxy, maxx],
        [miny, maxx],
        [miny, minx],
    ]
    return box


##############################################################################################################
def GetBoundMunicipio(nome_municipio: str, estado_sigla: str) -> list:
    """
    Função para obter o limite geográfico e o centroide de um município específico e retornar a Polyline.

    :param nome_municipio (str): Nome do município.
    :param estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).

    :return: Lista de coordenadas [(lat, lon), ...] representando o limite do município.
    """
    gdf = read_file("locationLimits")

    # Filtrar município e estado
    municipio = gdf[
        (gdf["NM_MUN"] == nome_municipio)
        & (gdf["CD_UF"] == uf.SIGLAS_UF[estado_sigla]["CD_UF"])
    ]

    if municipio.empty:
        print(
            f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado."
        )
        return None

    # Obter a geometria do município
    geometria = municipio.geometry.values[0]  # Geometria do limite
    # centroide = geometria.centroid  # Centroide do município

    # Extrair coordenadas como Polyline
    polyline = []
    if geometria.geom_type == "MultiPolygon":
        for polygon in geometria.geoms:
            polyline.append(list(polygon.exterior.coords))
    else:
        # Se for Polygon, apenas extrair as coordenadas
        polyline.append(list(geometria.exterior.coords))

    # Retornar a Polyline (como lista de coordenadas)
    return polyline


##############################################################################################################
def FiltrarComunidadesBoundingBox(bounding_box: tuple) -> list:
    """
    Filtra os dados de um shapefile com base em um bounding box e plota os dados filtrados.

    :param bounding_box: Tupla contendo os limites do bounding box (minx, miny, maxx, maxy)
    """
    # Carregar o arquivo Shapefile
    gdf = read_file("locationUrbanCommunities")

    # Criar um polígono representando o bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Filtrar os dados que estão dentro do bounding box
    data_filtrada = gdf[gdf.geometry.intersects(bbox_polygon)]

    polylines = []

    for geom in data_filtrada.geometry:
        if geom.is_empty:
            continue

        # Caso seja um Polygon, extrair o contorno externo
        if isinstance(geom, Polygon):
            polylines.append([(lat, lon) for lon, lat in geom.exterior.coords])

        # Caso seja um MultiPolygon, iterar sobre os polígonos internos
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:  # Acessar os polígonos do MultiPolygon
                polylines.append([(lat, lon) for lon, lat in poly.exterior.coords])

    return polylines


##############################################################################################################
def FiltrarAreasUrbanizadasPorMunicipio(municipio_nome: str, estado_sigla: str) -> list:
    """
    Filtra as áreas urbanizadas de um município específico e retorna as polylines correspondentes.

    :param municipio_nome (str): Nome do município.
    :param estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).

    :return: Lista de polylines representando as áreas urbanizadas do município.
    """
    # Carregar os shapefiles
    gdf_areas = read_file("locationUrbanAreas")
    gdf_municipios = read_file("locationLimits")

    # Filtrar o município pelo nome e estado
    municipio_filtrado = gdf_municipios[
        (gdf_municipios["NM_MUN"] == municipio_nome)
        & (gdf_municipios["CD_UF"] == uf.SIGLAS_UF[estado_sigla]["CD_UF"])
    ]

    # Garantir que os sistemas de coordenadas (CRS) são os mesmos
    # print(gdf_areas.crs, gdf_municipios.crs)
    if gdf_areas.crs != gdf_municipios.crs:
        gdf_areas = gdf_areas.to_crs(gdf_municipios.crs)

    # Criar um único polígono do município
    municipio_poligono = (
        municipio_filtrado.unary_union
    )  # Une todas as geometrias do município

    # Cortar as áreas urbanizadas que extrapolam o município
    gdf_areas["geometry"] = gdf_areas["geometry"].intersection(municipio_poligono)

    # Remover geometrias vazias (áreas que ficaram totalmente fora do município)
    gdf_areas = gdf_areas[~gdf_areas["geometry"].is_empty]

    # Filtrar pelas categorias de densidade
    densidades = ["Densa", "Pouco densa", "Loteamento vazio"]
    gdf_areas = gdf_areas[gdf_areas["densidade"].isin(densidades)]

    # Converter os polígonos em polylines (listas de coordenadas)
    polylines = []
    for geometry in gdf_areas["geometry"]:
        if geometry.is_empty:
            continue
        if geometry.geom_type == "Polygon":
            polylines.append(list(geometry.exterior.coords))  # Apenas o contorno
        elif geometry.geom_type == "MultiPolygon":
            for part in geometry.geoms:
                polylines.append(
                    list(part.exterior.coords)
                )  # Apenas o contorno de cada parte

    return polylines


##############################################################################################################
def ObterMunicipiosNoBoundingBox(bounding_box: tuple) -> list:
    """
    Retorna uma lista com os nomes dos municípios cuja geometria está inteiramente dentro do bounding box fornecido.

    :param bounding_box: Tupla (minx, miny, maxx, maxy)
    :return: Lista de strings no formato "Cidade-UF"
    """
    # Carrega o shapefile de municípios
    gdf = read_file("locationLimits")

    # Cria polígono do bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Filtra os municípios cuja geometria está inteiramente dentro do bounding box
    municipios_filtrados = gdf[gdf.geometry.within(bbox_polygon)]

    # Monta lista com chave "Cidade-UF"
    resultado = []
    for _, row in municipios_filtrados.iterrows():
        nome = row["NM_MUN"]
        codigo_uf = row["CD_UF"]
        sigla_uf = None
        for uf_sigla, dados in uf.SIGLAS_UF.items():
            if dados["CD_UF"] == codigo_uf:
                sigla_uf = uf_sigla
                break

        if sigla_uf:
            chave = f"{nome}-{sigla_uf}"
            resultado.append(chave)

    return resultado


##############################################################################################################


def ObterMunicipiosNoBoundingBoxOrdenados(bounding_box: tuple) -> list:
    """
    Retorna uma lista de dicionários com o nome do município, distância (em km) ao centro do bounding box,
    e uma flag indicando se está inteiramente dentro do bounding box.

    :param bounding_box: Tupla (minx, miny, maxx, maxy)
    :return: Lista de dicionários no formato:
             [{"location": "Cidade/UF", "dist": distância_km, "inBoundingBox": True}, ...]
    """
    # Carrega o shapefile de municípios
    gdf = read_file("locationLimits")

    # Cria polígono do bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Calcula o centro do bounding box
    centro_bbx = [(minx + maxx) / 2, (miny + maxy) / 2]

    # Função para calcular a distância entre dois pontos (em coordenadas geográficas)
    def calcular_distancia(ponto1, ponto2):
        return pyproj.Geod(ellps="WGS84").inv(
            ponto1[0], ponto1[1], ponto2[0], ponto2[1]
        )[2]

    resultado = []
    for _, row in gdf[gdf.geometry.intersects(bbox_polygon)].iterrows():
        nome = row["NM_MUN"]
        codigo_uf = row["CD_UF"]
        sigla_uf = None
        for uf_sigla, dados in uf.SIGLAS_UF.items():
            if dados["CD_UF"] == codigo_uf:
                sigla_uf = uf_sigla
                break

        if sigla_uf:
            municipio_centroid = row["geometry"].centroid
            centroid_coords = [municipio_centroid.x, municipio_centroid.y]
            distancia_km = calcular_distancia(centro_bbx, centroid_coords) / 1000.0

            location_str = f"{nome}"
            uf_str = f"{sigla_uf}"
            dentro = row["geometry"].within(bbox_polygon)

            resultado.append(
                {
                    "location": location_str,
                    "uf": uf_str,
                    "dist": round(distancia_km, 2),
                    "inBoundingBox": dentro,
                }
            )

    # Ordena pela distância
    resultado.sort(key=lambda x: x["dist"])

    return resultado
