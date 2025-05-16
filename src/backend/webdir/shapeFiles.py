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
import webRota as wr
import uf_code as uf

import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon
import uf_code as uf
import pyproj


SHAPEFILE_MUNICIPIO_PATH = "../../resources/BR_Municipios/BR_Municipios_2023.shp"
SHAPEFILE_FAVELA_PATH = "../../resources/Comunidades/qg_2022_670_fcu_agregPolygon.shp"
SHAPEFILE_AREA_URBANIZADA_PATH = (
    "../../resources/Urbanizacao/AU_2022_AreasUrbanizadas2019_Brasil.shp"
)


###########################################################################################################################
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/Brasil/BR_Municipios_2023.zip
##########################################################################################################################
def GetBoundMunicipio(nome_municipio: str, estado_sigla: str) -> list:
    """
    Função para obter o limite geográfico e o centroide de um município específico e retornar a Polyline.

    :param nome_municipio (str): Nome do município.
    :param estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).

    :return: Lista de coordenadas [(lat, lon), ...] representando o limite do município.
    """
    wr.wLog(f"GetBoundMunicipio - {nome_municipio},  {estado_sigla}")

    # Carregar o arquivo Shapefile BR_Municipios_2023.shp

    gdf = gpd.read_file(SHAPEFILE_MUNICIPIO_PATH)

    # Filtrar município e estado
    municipio = gdf[
        (gdf["NM_MUN"] == nome_municipio)
        & (gdf["CD_UF"] == uf.SIGLAS_UF[estado_sigla]["CD_UF"])
    ]

    if municipio.empty:
        wr.wLog(
            f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado.",level="debug"
        )
        return None

    # Obter a geometria do município
    geometria = municipio.geometry.values[0]  # Geometria do limite
    # centroide = geometria.centroid  # Centroide do município

    # Extrair coordenadas como Polyline
    polyline = []
    if geometria.geom_type == "MultiPolygon":
        # Se for MultiPolygon, concatenar coordenadas de todos os polígonos
        wr.wLog("Foi multipoligon - Cidade possui ilhas ou áreas isoladas",level="debug")

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
    data = gpd.read_file(SHAPEFILE_FAVELA_PATH)

    # Inspecionar os dados (opcional)
    # print("Primeiras linhas do shapefile:")
    # print(data.head())
    # print("\nSistema de Coordenadas:")
    # print(data.crs)
    # print("\nColunas da tabela de atributos:")
    # print(data.columns)

    # Criar um polígono representando o bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Filtrar os dados que estão dentro do bounding box
    data_filtrada = data[data.geometry.intersects(bbox_polygon)]

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

    # Imprimir a lista de polylines
    # for i, polyline in enumerate(polylines):
    #    print(f"Polyline {i+1}: {polyline}")

    return polylines


##############################################################################################################
def FiltrarAreasUrbanizadasPorMunicipio(municipio_nome: str, estado_sigla: str) -> list:
    """
    Filtra as áreas urbanizadas de um município específico e retorna as polylines correspondentes.

    :param municipio_nome (str): Nome do município.
    :param estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).

    :return: Lista de polylines representando as áreas urbanizadas do município.
    """

    wr.wLog(f"FiltrarAreasUrbanizadasPorMunicipio - {municipio_nome} - {estado_sigla}")

    # Carregar os shapefiles
    gdf_areas = gpd.read_file(SHAPEFILE_AREA_URBANIZADA_PATH)
    gdf_municipios = gpd.read_file(SHAPEFILE_MUNICIPIO_PATH)

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

    # print(gdf_areas['geometry'].is_empty.sum())  # Conta quantas geometrias vazias existem

    # Remover geometrias vazias (áreas que ficaram totalmente fora do município)
    gdf_areas = gdf_areas[~gdf_areas["geometry"].is_empty]

    # Filtrar pelas categorias de densidade
    densidades = ["Densa", "Pouco densa", "Loteamento vazio"]
    gdf_areas = gdf_areas[gdf_areas["densidade"].isin(densidades)]

    # print(gdf_areas[gdf_areas.intersects(municipio_poligono)])
    # print(gdf_areas['geometry'].geom_type.value_counts())

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
    import geopandas as gpd
    from shapely.geometry import box
    import uf_code as uf  # Certifique-se de que esse módulo está acessível

    # Carrega o shapefile de municípios
    gdf = gpd.read_file(SHAPEFILE_MUNICIPIO_PATH)

    # Cria polígono do bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Filtra os municípios cuja geometria está inteiramente dentro do bounding box
    municipios_filtrados = gdf[gdf.geometry.within(bbox_polygon)]

    # Monta lista com chave "Cidade-UF"
    resultado = []
    for _, row in municipios_filtrados.iterrows():
        nome = row['NM_MUN']
        codigo_uf = row['CD_UF']
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
    gdf = gpd.read_file(SHAPEFILE_MUNICIPIO_PATH)

    # Cria polígono do bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Calcula o centro do bounding box
    centro_bbx = [(minx + maxx) / 2, (miny + maxy) / 2]

    # Função para calcular a distância entre dois pontos (em coordenadas geográficas)
    def calcular_distancia(ponto1, ponto2):
        return pyproj.Geod(ellps="WGS84").inv(ponto1[0], ponto1[1], ponto2[0], ponto2[1])[2]
    
    resultado = []
    for _, row in gdf[gdf.geometry.intersects(bbox_polygon)].iterrows():
        nome = row['NM_MUN']
        codigo_uf = row['CD_UF']
        sigla_uf = None
        for uf_sigla, dados in uf.SIGLAS_UF.items():
            if dados["CD_UF"] == codigo_uf:
                sigla_uf = uf_sigla
                break

        if sigla_uf:
            municipio_centroid = row['geometry'].centroid
            centroid_coords = [municipio_centroid.x, municipio_centroid.y]
            distancia_km = calcular_distancia(centro_bbx, centroid_coords) / 1000.0

            location_str = f"{nome}"
            uf_str = f"{sigla_uf}"
            dentro = row['geometry'].within(bbox_polygon)

            resultado.append({
                "location": location_str,
                "uf": uf_str,
                "dist": round(distancia_km, 2),
                "inBoundingBox": dentro
            })

    # Ordena pela distância
    resultado.sort(key=lambda x: x["dist"])

    return resultado


##############################################################################################################