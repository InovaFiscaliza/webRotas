import geopandas as gpd

# Carregar o arquivo Shapefile
shapefile_path = "../../Comunidades/qg_2022_670_fcu_agregPolygon.shp"
data = gpd.read_file(shapefile_path)

# Inspecionar os dados
print(data.head())  # Primeiras linhas do shapefile
print(data.crs)     # Sistema de coordenadas
print(data.columns) # Colunas da tabela de atributos


import matplotlib.pyplot as plt
from shapely.geometry import box  # Certifique-se de importar aqui

# Definir os limites do bounding box para Niterói
minx, miny, maxx, maxy = -43.1363, -22.9488, -43.0329, -22.8708

# Criar um polígono representando o bounding box
bounding_box = box(minx, miny, maxx, maxy)

# Filtrar os dados que estão dentro do bounding box
data_filtrada = data[data.geometry.intersects(bounding_box)]

# Plotar os dados filtrados
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
data_filtrada.plot(ax=ax, color="blue", edgecolor="black")
plt.title("Área Filtrada: Niterói (RJ)")
plt.show()