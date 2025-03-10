import geopandas as gpd
import matplotlib.pyplot as plt 
import geopandas as gpd
from shapely.geometry import Polygon, LineString

def plotar_areas_filtradas(areas_filtradas):
    areas_filtradas.plot()
    plt.title("Áreas urbanizadas filtradas")
    plt.show()

# Dentro da sua função, após filtrar as áreas:


# Função para filtrar áreas urbanas por município e densidade
def filtrar_por_municipio(caminho_shapefile_areas, caminho_shapefile_municipios, municipio_nome, estado_sigla):
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
    areas_no_municipio = gpd.sjoin(gdf_areas, municipio_filtrado, op='within')
    
    # Filtrar pelas categorias de densidade
    densidades = ['Densa', 'Pouco densa', 'Loteamento vazio']
    areas_filtradas_por_densidade = areas_no_municipio[areas_no_municipio['densidade'].isin(densidades)]
    
    # Exibir o resultado filtrado por densidade
    print(f"Áreas urbanizadas filtradas para o município {municipio_nome} e densidades {densidades}:")
    print(areas_filtradas_por_densidade)
    
    # Converter as geometrias de polígonos em polylines
    polylines = []
    for geometry in areas_filtradas_por_densidade['geometry']:
        if isinstance(geometry, Polygon):  # Garantir que é um polígono
            polylines.append(LineString(geometry.exterior.coords))  # Converter para linha (polyline)
        elif geometry.geom_type == 'MultiPolygon':  # Se for um multipolígono
            for part in geometry.geoms:
                polylines.append(LineString(part.exterior.coords))  # Converter para linha (polyline)
    
    # Exibir as polylines geradas
    print(f"Polylines geradas para as áreas filtradas:")
    print(polylines)
    

    # Retornar as polylines
    return polylines





def depurar_shapefile(caminho_shapefile):
    # Carregar o shapefile
    gdf = gpd.read_file(caminho_shapefile)

    # Exibir informações gerais sobre o shapefile
    print("Estrutura do Shapefile:")
    print("-" * 50)
    
    # Exibe as primeiras 5 linhas (ou registros) do shapefile
    print("Primeiros registros:")
    print(gdf.head())
    
    # Exibe informações gerais sobre o GeoDataFrame (tipo de dados, colunas, etc.)
    print("\nInformações gerais do GeoDataFrame:")
    print(gdf.info())
    
    # Exibe as colunas presentes no shapefile
    print("\nColunas disponíveis:")
    print(gdf.columns)
    
    # Exibe o sistema de referência de coordenadas (CRS) do shapefile
    print("\nSistema de Referência de Coordenadas (CRS):")
    print(gdf.crs)

    # Verificar se há geometria presente no shapefile
    print("\nPrimeiros valores da geometria:")
    print(gdf.geometry.head())

    # Listar todos os tipos de densidade presentes na coluna 'densidade'
    print("\nTipos de densidade presentes:")
    print(gdf['densidade'].unique())
    
    # Listar todos os tipos presentes na coluna 'tipo'
    print("\nTipos presentes na coluna 'tipo':")
    print(gdf['tipo'].unique())
    
    # Listar todos os valores presentes na coluna 'comparacao'
    print("\nValores presentes na coluna 'comparacao':")
    print(gdf['comparacao'].unique())

# Chamar a função com o caminho do seu shapefile
shapefile_path = "AU_2022_AreasUrbanizadas2019_Brasil.shp"
depurar_shapefile(shapefile_path)



# Exemplo de uso da função
shapefile_areas_path = "AU_2022_AreasUrbanizadas2019_Brasil.shp"
shapefile_municipios_path = "../BR_Municipios_2022/BR_Municipios_2022.shp"
municipio_nome = "Niterói"  # Substitua pelo nome do município que você deseja filtrar
estado_sigla="RJ"
filtrar_por_municipio(shapefile_areas_path, shapefile_municipios_path, municipio_nome,estado_sigla)