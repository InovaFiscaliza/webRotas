###########################################################################################################################
import WebRota as wr
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
from shapely.geometry import Polygon, MultiPolygon

###########################################################################################################################
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip
##########################################################################################################################
def GetBoundMunicipio(nome_municipio, estado_sigla):
    """
    Função para obter o limite geográfico e o centroide de um município específico e retornar a Polyline.
    
    Parâmetros:
        nome_municipio (str): Nome do município.
        estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).
        
    Retorna:
        polyline (list): Lista de coordenadas [(lat, lon), ...] representando o limite do município.
        centroide (Point): Coordenadas do centroide do município.
    """
    wr.wLog(f"GetBoundMunicipio - {nome_municipio} - {estado_sigla}")
    # Carregar o arquivo Shapefile BR_Municipios_2022.shp
    shapefile_path = '../../resources/BR_Municipios_2022/BR_Municipios_2022.shp'
    gdf = gpd.read_file(shapefile_path)
    
    # Filtrar município e estado
    municipio = gdf[(gdf['NM_MUN'] == nome_municipio) & (gdf['SIGLA_UF'] == estado_sigla)]

    if municipio.empty:
        wr.wLog(f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado.")
        return None
    
    # Obter a geometria do município
    geometria = municipio.geometry.values[0]  # Geometria do limite
    centroide = geometria.centroid            # Centroide do município
    
    # Extrair coordenadas como Polyline
    polyline = []
    if geometria.geom_type == 'MultiPolygon':
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
def FiltrarComunidadesBoundingBox(bounding_box):
    """
    Filtra os dados de um shapefile com base em um bounding box e plota os dados filtrados.

    :param shapefile_path: Caminho para o arquivo Shapefile (.shp)
    :param bounding_box: Lista ou tupla contendo os limites do bounding box (minx, miny, maxx, maxy)
    """
    # Caminho para o arquivo Shapefile
    shapefile_path = "../../resources/Comunidades/qg_2022_670_fcu_agregPolygon.shp"
    # Carregar o arquivo Shapefile
    data = gpd.read_file(shapefile_path)

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
    #for i, polyline in enumerate(polylines):
    #    print(f"Polyline {i+1}: {polyline}")
        
    return polylines

##############################################################################################################
def main():
    """
    Função principal para executar o script.
    """


    # Definir os limites do bounding box para Niterói (RJ)
    bounding_box = (-43.1363, -22.9488, -43.0329, -22.8708)

    # Chamar a função para filtrar e plotar
    dados=FiltrarComunidadesBoundingBox(bounding_box)
    
     # Plotar os dados filtrados
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    dados.plot(ax=ax, color="blue", edgecolor="black")
    plt.title("Área Filtrada")
    plt.show()   
##############################################################################################################
if __name__ == "__main__":
    main()
##############################################################################################################