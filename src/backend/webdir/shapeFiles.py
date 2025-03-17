###########################################################################################################################
import webRota as wr
import uf_code as uf

import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon

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
            f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado."
        )
        return None

    # Obter a geometria do município
    geometria = municipio.geometry.values[0]  # Geometria do limite
    # centroide = geometria.centroid  # Centroide do município

    # Extrair coordenadas como Polyline
    polyline = []
    if geometria.geom_type == "MultiPolygon":
        # Se for MultiPolygon, concatenar coordenadas de todos os polígonos
        wr.wLog("Foi multipoligon - Cidade possui ilhas ou áreas isoladas")

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


##############################################################################################################
# Função para filtrar áreas urbanas por município
def FiltrarAreasUrbanizadasPorMunicipioOLD(
    municipio_nome: str, estado_sigla: str
) -> list:
    """Filtra as áreas urbanizadas de um município específico e retorna as polylines correspondentes.

    :param municipio_nome (str): Nome do município.
    :param estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).

    :return: Lista de polylines representando as áreas urbanizadas do município.
    """

    # Carregar os shapefiles
    gdf_areas = gpd.read_file(SHAPEFILE_AREA_URBANIZADA_PATH)
    gdf_municipios = gpd.read_file(SHAPEFILE_MUNICIPIO_PATH)

    # Filtrar o município desejado (por nome ou código)
    municipio_filtrado = gdf_municipios[
        (gdf_municipios["NM_MUN"] == municipio_nome)
        & (gdf_municipios["CD_UF"] == uf.SIGLAS_UF[estado_sigla]["CD_UF"])
    ]

    # Verificar se o CRS dos dois shapefiles é o mesmo
    if gdf_areas.crs != gdf_municipios.crs:
        gdf_areas = gdf_areas.to_crs(gdf_municipios.crs)

    # Realizar a interseção espacial entre as áreas urbanizadas e o município
    # areas_no_municipio = gpd.sjoin(gdf_areas, municipio_filtrado, op='within')
    areas_no_municipio = gpd.sjoin(
        gdf_areas, municipio_filtrado, predicate="intersects"
    )

    # Filtrar pelas categorias de densidade
    # densidades = ['Densa', 'Pouco densa', 'Loteamento vazio']
    # areas_filtradas_por_densidade = areas_no_municipio[areas_no_municipio['densidade'].isin(densidades)]

    areas_filtradas_por_densidade = areas_no_municipio

    # Exibir o resultado filtrado por densidade
    # print(f"Áreas urbanizadas filtradas para o município {municipio_nome} e densidades {densidades}:")
    # print(areas_filtradas_por_densidade)

    # Converter as geometrias de polígonos em polylines
    polylines = []
    for geometry in areas_filtradas_por_densidade["geometry"]:
        if isinstance(geometry, Polygon):
            polylines.append(
                list(geometry.exterior.coords)
            )  # Transforma em lista de coordenadas
        elif geometry.geom_type == "MultiPolygon":
            for part in geometry.geoms:
                polylines.append(
                    list(part.exterior.coords)
                )  # Transforma em lista de coordenadas

    # Exibir as polylines geradas
    # print(f"Polylines geradas para as áreas filtradas:")
    # print(polylines)

    # Retornar as polylines
    return polylines


##############################################################################################################
