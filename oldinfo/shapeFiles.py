###########################################################################################################################
import webRota as wr
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
from shapely.geometry import Polygon, MultiPolygon


###########################################################################################################################
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip
##########################################################################################################################

##############################################################################################################
# Função para filtrar áreas urbanas por município  
def FiltrarAreasUrbanizadasPorMunicipio(municipio_nome, estado_sigla):    
    caminho_shapefile_areas = "../../resources/Urbanizacao/AU_2022_AreasUrbanizadas2019_Brasil.shp"
    caminho_shapefile_municipios = "../../resources/BR_Municipios_2022/BR_Municipios_2022.shp"
    
    # Carregar o shapefile de áreas urbanizadas
    gdf_areas = gpd.read_file(caminho_shapefile_areas)
    
    # Carregar o shapefile de limites municipais
    gdf_municipios = gpd.read_file(caminho_shapefile_municipios)
    
    # Filtrar o município desejado (por nome ou código)
    municipio_filtrado = gdf_municipios[(gdf_municipios['NM_MUN'] == municipio_nome) & (gdf_municipios['SIGLA_UF'] == estado_sigla)]
    
    # Verificar se o CRS dos dois shapefiles é o mesmo
    if gdf_areas.crs != gdf_municipios.crs:
        gdf_areas = gdf_areas.to_crs(gdf_municipios.crs)
    
    # Realizar a interseção espacial entre as áreas urbanizadas e o município
    # areas_no_municipio = gpd.sjoin(gdf_areas, municipio_filtrado, op='within')
    areas_no_municipio = gpd.sjoin(gdf_areas, municipio_filtrado, predicate='intersects')

    
    # Filtrar pelas categorias de densidade
    # densidades = ['Densa', 'Pouco densa', 'Loteamento vazio']
    # areas_filtradas_por_densidade = areas_no_municipio[areas_no_municipio['densidade'].isin(densidades)]
    
    areas_filtradas_por_densidade = areas_no_municipio
    
    # Exibir o resultado filtrado por densidade
    # print(f"Áreas urbanizadas filtradas para o município {municipio_nome} e densidades {densidades}:")
    # print(areas_filtradas_por_densidade)
    
    # Converter as geometrias de polígonos em polylines
    polylines = []
    for geometry in areas_filtradas_por_densidade['geometry']:
        if isinstance(geometry, Polygon):  
            polylines.append(list(geometry.exterior.coords))  # Transforma em lista de coordenadas
        elif geometry.geom_type == 'MultiPolygon':  
            for part in geometry.geoms:
                polylines.append(list(part.exterior.coords))  # Transforma em lista de coordenadas
  
    
    # Exibir as polylines geradas
    # print(f"Polylines geradas para as áreas filtradas:")
    # print(polylines)
    

    # Retornar as polylines
    return polylines
##############################################################################################################
