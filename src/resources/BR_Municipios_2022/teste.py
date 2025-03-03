import geopandas as gpd
import matplotlib.pyplot as plt

# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip


##########################################################################################################################
def ObterLimiteMunicipioPol(nome_municipio, estado_sigla):
    """
    Função para obter o limite geográfico e o centroide de um município específico e retornar a Polyline.
    
    Parâmetros:
        nome_municipio (str): Nome do município.
        estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).
        
    Retorna:
        polyline (list): Lista de coordenadas [(lat, lon), ...] representando o limite do município.
        centroide (Point): Coordenadas do centroide do município.
    """
    
    # Carregar o arquivo Shapefile BR_Municipios_2022.shp
    shapefile_path = 'BR_Municipios_2022.shp'
    gdf = gpd.read_file(shapefile_path)
    
    # Filtrar município e estado
    municipio = gdf[(gdf['NM_MUN'] == nome_municipio) & (gdf['SIGLA_UF'] == estado_sigla)]

    if municipio.empty:
        print(f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado.")
        return None, None
    
    # Obter a geometria do município
    geometria = municipio.geometry.values[0]  # Geometria do limite
    centroide = geometria.centroid            # Centroide do município
    
    # Extrair coordenadas como Polyline
    if geometria.geom_type == 'MultiPolygon':
        # Se for MultiPolygon, concatenar coordenadas de todos os polígonos
        polyline = []
        for polygon in geometria.geoms:
            polyline.extend(list(polygon.exterior.coords))
    else:
        # Se for Polygon, apenas extrair as coordenadas
        polyline = list(geometria.exterior.coords)
    
    # Retornar a Polyline (como lista de coordenadas) e o centroide
    return polyline
##########################################################################################################################
# Exemplo de uso
nome_municipio = 'Niterói'
estado_sigla = 'RJ'

polyline, centroide = obter_limite_municipioPol(nome_municipio, estado_sigla)

if polyline:
    print(f"Polyline do município de {nome_municipio}: {polyline[:5]}...")  # Mostrar apenas os 5 primeiros pontos
    print(f"Centroide: {centroide}")

##########################################################################################################################
def obter_limite_municipio(nome_municipio, estado_sigla):
    """
    Função para obter o limite geográfico e o centroide de um município específico.
    
    Parâmetros:
        nome_municipio (str): Nome do município.
        estado_sigla (str): Sigla do estado (ex: 'RJ' para Rio de Janeiro).
        
    Retorna:
        gdf (GeoDataFrame): Dados geoespaciais do município.
        centroide (Point): Coordenadas do centroide do município.
    """
    
 
    
    # Carregar o arquivo Shapefile BR_Municipios_2022.shp
    shapefile_path = 'BR_Municipios_2022.shp'
    gdf = gpd.read_file(shapefile_path)
    print(gdf.columns) # depurar as colunas
    
    # Filtrar município e estado
    municipio = gdf[(gdf['NM_MUN'] == nome_municipio) & (gdf['SIGLA_UF'] == estado_sigla)]

    if municipio.empty:
        print(f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado.")
        return None, None
    
    # Calcular o centroide
    centroide = municipio.geometry.centroid

    # Plotar o limite do município
    municipio.plot(figsize=(8, 8), edgecolor='black', color='lightblue')
    plt.title(f'Limite Municipal de {nome_municipio} - {estado_sigla}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

    # Retornar o GeoDataFrame e o centroide
    return municipio, centroide
##########################################################################################################################
# Exemplo de uso da função
municipio, centroide = obter_limite_municipio('Niterói', 'RJ')

# Exibir as coordenadas do centroide
if municipio is not None:
    print(f"Coordenadas do centroide de Niterói: {centroide}")
