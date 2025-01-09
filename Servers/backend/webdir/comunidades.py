
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
##############################################################################################################
def FiltrarComunidadesBoundingBox(bounding_box):
    """
    Filtra os dados de um shapefile com base em um bounding box e plota os dados filtrados.

    :param shapefile_path: Caminho para o arquivo Shapefile (.shp)
    :param bounding_box: Lista ou tupla contendo os limites do bounding box (minx, miny, maxx, maxy)
    """
    # Caminho para o arquivo Shapefile
    shapefile_path = "../../Comunidades/qg_2022_670_fcu_agregPolygon.shp"
    # Carregar o arquivo Shapefile
    data = gpd.read_file(shapefile_path)

    # Inspecionar os dados (opcional)
    print("Primeiras linhas do shapefile:")
    print(data.head())
    print("\nSistema de Coordenadas:")
    print(data.crs)
    print("\nColunas da tabela de atributos:")
    print(data.columns)

    # Criar um polígono representando o bounding box
    minx, miny, maxx, maxy = bounding_box
    bbox_polygon = box(minx, miny, maxx, maxy)

    # Filtrar os dados que estão dentro do bounding box
    data_filtrada = data[data.geometry.intersects(bbox_polygon)]

    # Verificar se há dados filtrados
    if data_filtrada.empty:
        print("Nenhum dado encontrado dentro do bounding box.")
        return None
    return data_filtrada

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