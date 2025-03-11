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


NOVA solução chargpt

Para garantir que as áreas urbanizadas dentro de um município sejam mantidas e as partes que se estendem para fora sejam cortadas na fronteira do município, podemos usar a operação interseção (intersection) do GeoPandas.
🔹 Passos principais:

    Carregar os shapefiles das áreas urbanizadas e do município.
    Filtrar o município desejado pelo nome e estado.
    Garantir que ambos os datasets estão no mesmo CRS.
    Usar intersection para cortar as áreas urbanizadas na fronteira do município.

🎯 O que essa versão faz de diferente?

✅ Corta as partes das áreas urbanizadas que estão fora do município.
✅ Mantém as partes das áreas urbanizadas dentro do município.
✅ Descarta áreas que ficaram totalmente fora do município.
✅ Retorna polylines para representar os contornos das áreas urbanizadas cortadas.

🔹 Agora, mesmo que uma área urbanizada ultrapasse os limites municipais, apenas a parte dentro da cidade será mantida e usada.

🏗 Código atualizado para cortar as áreas urbanizadas na fronteira do município


import geopandas as gpd

def FiltrarAreasUrbanizadasPorMunicipio(municipio_nome, estado_sigla):    
    caminho_shapefile_areas = "../../resources/Urbanizacao/AU_2022_AreasUrbanizadas2019_Brasil.shp"
    caminho_shapefile_municipios = "../../resources/BR_Municipios_2022/BR_Municipios_2022.shp"
    
    # Carregar os shapefiles
    gdf_areas = gpd.read_file(caminho_shapefile_areas)
    gdf_municipios = gpd.read_file(caminho_shapefile_municipios)
    
    # Filtrar o município pelo nome e estado
    municipio_filtrado = gdf_municipios[(gdf_municipios['NM_MUN'] == municipio_nome) & 
                                        (gdf_municipios['SIGLA_UF'] == estado_sigla)]
    
    # Garantir que os sistemas de coordenadas (CRS) são os mesmos
    if gdf_areas.crs != gdf_municipios.crs:
        gdf_areas = gdf_areas.to_crs(gdf_municipios.crs)

    # Criar um único polígono do município
    municipio_poligono = municipio_filtrado.unary_union  # Une todas as geometrias do município
    
    # Cortar as áreas urbanizadas que extrapolam o município
    gdf_areas['geometry'] = gdf_areas['geometry'].intersection(municipio_poligono)

    # Remover geometrias vazias (áreas que ficaram totalmente fora do município)
    gdf_areas = gdf_areas[~gdf_areas['geometry'].is_empty]
    
    # Converter os polígonos em polylines (listas de coordenadas)
    polylines = []
    for geometry in gdf_areas['geometry']:
        if geometry.is_empty:
            continue
        if geometry.geom_type == 'Polygon':  
            polylines.append(list(geometry.exterior.coords))  # Apenas o contorno
        elif geometry.geom_type == 'MultiPolygon':  
            for part in geometry.geoms:
                polylines.append(list(part.exterior.coords))  # Apenas o contorno de cada parte
  
    return polylines
