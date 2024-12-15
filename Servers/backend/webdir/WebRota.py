###########################################################################################################################
import GeraMapa as gm

# Salvar enviroment
# conda env export > environment.yml

# Criar em outro computador
# conda env create -f environment.yml

# https://github.com/anaconda/docker-images

# import folium # pip install folium
import math
import subprocess
import requests
import polyline # pip install polyline
import simplekml # pip install simplekml
import json


# conda create --name webrotas python=3.11
# conda activate webrotas

# from osgeo import ogr # conda install -c conda-forge gdal 
                      # conda install conda-forge::gdal 
                      # conda install -c conda-forge gdal=3.0.2
                      # set USE_PATH_FOR_GDAL_PYTHON=YES
                      # set PATH=%PATH%;C:\Users\andre\anaconda3\Library\bin
###########################################################################################################################
def GerarGeojson(coordenadas, filename="output.geojson"):
    # Estrutura GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat, lon in coordenadas]  # GeoJSON usa formato [longitude, latitude]
                },
                "properties": {
                    "name": "Rota"
                }
            }
        ]
    }

    # Salvar arquivo GeoJSON
    with open(filename, 'w') as geojson_file:
        json.dump(geojson_data, geojson_file, indent=4)
    wLog(f"Arquivo {filename} gerado com sucesso!")
                      
###########################################################################################################################
def GetCurl(url):
    # função criada para resolver o problema do requests.get(url) não funcionar no locahost do OpenRoute
    result = subprocess.run(
    ["curl", "-X", "GET", url, "-H", "Accept: application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8"],
    capture_output=True,
    text=True
    )
    ret = result
    ret.status_code = result.stdout
    ret.reason = result.stderr
    return result.stdout
###########################################################################################################################
class ClRouteDetail:
    # The constructor method
    def __init__(self, lat, lon,street):
        self.lat = lat 
        self.lon = lon
        self.street = street
        self.azimute = 0
        self.distm = 0
        
###########################################################################################################################
class ClRouteDetailList:
    def __init__(self):
        self.list = []
        self.ind=0    
        self.waypnts = [] 
        self.instructions = [] 
        self.coordinates = []
        self.mapcode = ""    
    #---------------------------------------------------    
    def NewPiece(self, lat, lon,street):   
       self.list.append(ClRouteDetail(lat, lon,street))
       if self.ind>0:
          lati = self.list[self.ind-1].lat
          loni = self.list[self.ind-1].lon
          latf = self.list[self.ind].lat
          lonf = self.list[self.ind].lon
          self.list[self.ind-1].azimute = Azimute(lati,loni,latf,lonf) 
          self.list[self.ind-1].distm = Haversine(lati,loni,latf,lonf)   # Em metros
          
          wLog(f"Trecho anterior = {self.list[self.ind-1].street} , Azim = {self.list[self.ind-1].azimute}, distm {self.list[self.ind-1].distm}")
          
       else:
          wLog("Primeiro trecho rota")    
       self.ind=self.ind+1
       return
    #---------------------------------------------------
    def GeraMapPolylineCaminho(self):
        wLog("Plotando polyline rota")
        self.mapcode += "\n"
        self.mapcode += """var poly_line = L.polyline(["""
        
        for i, (lat, lon) in enumerate(self.coordinates):
            if i == len(self.coordinates) - 1:  # Último elemento
               self.mapcode += f"[{lat}, {lon}]"
            else:
               self.mapcode += f"[{lat}, {lon}], "
          
        self.mapcode += """],{"bubblingMouseEvents": true, "color": "blue", "dashArray": null, "dashOffset": null, "fill": false, "fillColor": "blue", "fillOpacity": 0.2, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "noClip": false, "opacity": 0.7, "smoothFactor": 1.0, "stroke": true, "weight": 3}
                           ).addTo(map);\n"""
        return
    #---------------------------------------------------
    def NewWaypoint(self,waypoint,lat,lon):
        self.waypnts.append(ClRouteDetail(lat, lon,waypoint))
        return
    #---------------------------------------------------
    def NewInstruction(self,string):
        self.instructions.append(string)
        return
    #---------------------------------------------------
    # Função para imprimir todos os waypoints
    def PrintWaypoints(self):
        if len(self.waypnts) == 0:
            wLog("Nenhum waypoint adicionado.")
        else:
            wLog("Waypoints:")
            for idx, waypoint in enumerate(self.waypnts):
                wLog(f"{idx + 1}. Nome: {waypoint.street}, Latitude: {waypoint.lat}, Longitude: {waypoint.lon}")
        return        
###########################################################################################################################
def Haversine(lat1, lon1, lat2, lon2):
    # Raio da Terra em metros
    R = 6371000
    
    # Converter graus para radianos
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Diferenças das coordenadas
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    
    # Fórmula de Haversine
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distância em metros
    distancia = R * c
    
    return distancia
###########################################################################################################################
def Azimute(lat1, lon1, lat2, lon2):
    # Converter graus para radianos
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Calcular a diferença de longitudes
    delta_lon = lon2 - lon1
    
    # Calcular o azimute
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
    azimute = math.atan2(x, y)
    
    # Converter de radianos para graus
    azimute = math.degrees(azimute)
    
    # Normalizar o azimute para um intervalo de 0 a 360 graus
    azimute = (azimute + 360) % 360
    
    return azimute

###########################################################################################################################
def ReverseGeocode(lat, lon):
    return 'Rua não encontrada'
    driver = ogr.GetDriverByName('OSM')
    dataSource = driver.Open('./MapaBrasil/brazil-latest.osm.pbf', 0)
    layer = dataSource.GetLayer()

    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)

    layer.SetSpatialFilter(point)
    for feature in layer:
        if feature.GetField('name'):
            return feature.GetField('name')

    return 'Rua não encontrada'

# Exemplo de uso
# lat = -22.941704
# lon = -43.370423
# print(ReverseGeocode(lat, lon))
###########################################################################################################################

###########################################################################################################################
def GerarKml(coordenadas, filename="rota.kml"):
    # Criar um objeto KML
    kml = simplekml.Kml()

    # Adicionar uma linha ao KML com as coordenadas decodificadas
    linha = kml.newlinestring(name="Rota")
    linha.coords = coordenadas  # Adiciona as coordenadas à linha
    linha.extrude = 1  # Mantém a extrusão, mas sem altitude
    linha.style.linestyle.color = simplekml.Color.red  # Cor da linha
    linha.style.linestyle.width = 3  # Largura da linha

    # Salvar o arquivo KML
    kml.save(filename)

    # Para garantir que as coordenadas apareçam em linhas separadas no arquivo KML
    with open(filename, 'r') as file:
        content = file.read()
    
    # Remover todas as coordenadas da linha
    start = content.index('<coordinates>') + len('<coordinates>')
    end = content.index('</coordinates>')
    coords_string = content[start:end].strip()
    
    # Adicionar quebras de linha entre as coordenadas
    coords_string = '\n'.join([line.strip() for line in coords_string.split(' ')])

    # Escrever de volta o conteúdo com as coordenadas formatadas
    with open(filename, 'w') as file:
        content = content.replace(content[start:end], '\n' + coords_string + '\n')
        file.write(content)

    wLog(f"Arquivo {filename} gerado com sucesso!")
###########################################################################################################################
ServerTec = "OSMR"
# ServerTec = "GHopper"
# http://localhost:8989/route?point=-22.88945995932843,-43.10142517089844&point=-22.890725107354616,-43.06228637695313 
###########################################################################################################################
def GetRouteFromServer(start_lat, start_lon, end_lat, end_lon):
   # 
   # Coordenadas de início e fim   
   start_coords = (start_lat, start_lon)
   end_coords = (end_lat, end_lon)
   
   if ServerTec == "OSMR":
      # URL da solicitação ao servidor OSRM
      url = f"http://localhost:{UserData.OSMRport}/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline&steps=true"
   if ServerTec == "GHopper":
      # URL da solicitação ao servidor GHopper
      url = f"http://localhost:8989/route?point={start_lat},{start_lon}&point={end_lat},{end_lon}"
   
   wLog(url)
   # Fazer a solicitação
   response = requests.get(url)   
   return response
###########################################################################################################################
import os
import time
from datetime import datetime, timedelta
###########################################################################################################################
def DeleteOldFilesAndFolders(directory, days=30):
    """
    Remove arquivos e pastas (inclusive não vazias) mais antigos que um número específico de dias.

    Args:
        directory (str): Caminho para o diretório base.
        days (int): Número de dias para considerar como o limite. Padrão é 30.
        
    DeleteOldFilesAndFolders("/caminho/para/seu/diretorio", days=30)    
    """
    try:
        # Calcula a data limite
        now = time.time()
        cutoff = now - (days * 86400)  # 86400 segundos por dia

        # Itera pelos itens no diretório
        for filename in os.listdir(directory):
            item_path = os.path.join(directory, filename)

            # Obtém o tempo de modificação do item
            item_mtime = os.path.getmtime(item_path)

            # Verifica se é um arquivo
            if os.path.isfile(item_path) and item_mtime < cutoff:
                os.remove(item_path)
                print(f"Arquivo removido: {item_path}")

            # Verifica se é um diretório
            elif os.path.isdir(item_path) and item_mtime < cutoff:
                # Remove o diretório e todo o seu conteúdo
                shutil.rmtree(item_path)  # Remove diretórios e seus conteúdos
                print(f"Pasta removida: {item_path}")
    except Exception as e:
        print(f"Erro ao processar o diretório: {e}")
###########################################################################################################################
def GenerateRouteMap(RouteDetailLoc,start_lat, start_lon, end_lat, end_lon):
    if ServerTec == "OSMR":
        return GenerateRouteMapOSMR(RouteDetailLoc,start_lat, start_lon, end_lat, end_lon)
    if ServerTec == "GHopper":
        return GenerateRouteMapGHopper(RouteDetailLoc,start_lat, start_lon, end_lat, end_lon)
    return RouteDetailLoc
###########################################################################################################################
def GenerateRouteMapGHopper(RouteDetailLoc,start_lat, start_lon, end_lat, end_lon):
    response = GetRouteFromServer(start_lat, start_lon, end_lat, end_lon)
    data = response.json()
    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200 and 'paths' in data:
       geometry =  data["paths"][0]["points"]
       coordinates = polyline.decode(geometry)
       RouteDetailLoc.coordinates += coordinates
       instructions = data["paths"][0]["instructions"]
       wLog("Imprimindo rota")    
       for step in instructions:
            RouteDetailLoc.NewInstruction(step['text'])    
            wLog(f"{step['text']}")        
    else:
       wLog(f"Erro na solicitação: {data}")    
       return RouteDetailLoc
            
    return RouteDetailLoc
###########################################################################################################################
import geopandas as gpd
import matplotlib.pyplot as plt
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
    wLog(f"GetBoundMunicipio - {nome_municipio} - {estado_sigla}")
    # Carregar o arquivo Shapefile BR_Municipios_2022.shp
    shapefile_path = '../../BR_Municipios_2022/BR_Municipios_2022.shp'
    gdf = gpd.read_file(shapefile_path)
    
    # Filtrar município e estado
    municipio = gdf[(gdf['NM_MUN'] == nome_municipio) & (gdf['SIGLA_UF'] == estado_sigla)]

    if municipio.empty:
        wLog(f"Município '{nome_municipio}' no estado '{estado_sigla}' não encontrado.")
        return None
    
    # Obter a geometria do município
    geometria = municipio.geometry.values[0]  # Geometria do limite
    centroide = geometria.centroid            # Centroide do município
    
    # Extrair coordenadas como Polyline
    polyline = []
    if geometria.geom_type == 'MultiPolygon':
        # Se for MultiPolygon, concatenar coordenadas de todos os polígonos
        wLog("Foi multipoligon - Cidade possui ilhas ou áreas isoladas")
        
        for polygon in geometria.geoms:
            polyline.append(list(polygon.exterior.coords))
    else:
        # Se for Polygon, apenas extrair as coordenadas
        polyline.append(list(geometria.exterior.coords))
    
    # Retornar a Polyline (como lista de coordenadas) 
    return polyline

###########################################################################################################################
def GenerateRouteMapOSMR(RouteDetailLoc,start_lat, start_lon, end_lat, end_lon):
    """
    Gera um mapa com uma rota entre dois pontos usando Folium e OpenRouteService.

    Args:
    - start_lat (float): Latitude do ponto de partida.
    - start_lon (float): Longitude do ponto de partida.
    - end_lat (float): Latitude do ponto de chegada.
    - end_lon (float): Longitude do ponto de chegada.
    - api_key (str): Chave de API para o serviço de roteamento (por exemplo, OpenRouteService).

    Returns:
    - folium.Map: Mapa com a rota plotada.
    """

    response = GetRouteFromServer(start_lat, start_lon, end_lat, end_lon)
    data = response.json()
    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200 and 'routes' in data:
       route = data['routes'][0]
       geometry = route['geometry']
       coordinates = polyline.decode(geometry)
       RouteDetailLoc.coordinates += coordinates
       # Pegando nomes das ruas e rota
       # waypoints = data['waypoints']

       # GerarKml(coordinates, filename="rota.kml")    
       # GerarGeojson(coordinates, filename="rota.geojson")
       wLog("Imprimindo rota")    
       nomes_ruas = []
       for route in data.get("routes", []):
         for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                mode = step.get("mode", "")	
                nome = step.get("name", "")
                destinations = step.get("destinations", "")
                tempo = step.get("duration", "")
                dist = step.get("distance", "")
                maneuver = step.get("maneuver", [])
                type = maneuver.get("type", "")
                modifier = maneuver.get("modifier", "")	
                location = maneuver.get("location", [])      
                # NewWaypoint(self,waypoint,lat,lon)
                RouteDetailLoc.NewWaypoint(f"{nome} {destinations}",str(location[1]),str(location[0]))
                wLog(f"{mode} {nome} {destinations} por {dist} metros e {tempo} segundos e {type} {modifier}")        
    else:
       wLog(f"Erro na solicitação: {data}")    
       return RouteDetailLoc
            
    return RouteDetailLoc
###########################################################################################################################
# Exemplo de uso
# start_lat = -23.55052   # Latitude de São Paulo, Brasil
# start_lon = -46.633308  # Longitude de São Paulo, Brasil
# end_lat = -23.5733      # Latitude de um ponto próximo em São Paulo, Brasil
# end_lon = -46.6417      # Longitude de um ponto próximo em São Paulo, Brasil
# api_key = 'YOUR_API_KEY'  # Substitua pela sua chave de API do OpenRouteService

# Gera o mapa com a rota
# map_with_route = generate_route_map(start_lat, start_lon, end_lat, end_lon, api_key)

# Salva o mapa em um arquivo HTML
# map_with_route.save('route_map.html')  
    
###########################################################################################################################
def GeneratePointsAround(latitude, longitude, radius_km=5, num_points=8):
    """
    Gera coordenadas de pontos em torno de um ponto central (latitude, longitude) em um raio especificado.

    Args:
    - latitude (float): Latitude do ponto central.
    - longitude (float): Longitude do ponto central.
    - radius_km (float): Raio em quilômetros para gerar os pontos ao redor.
    - num_points (int): Número de pontos para gerar ao redor do ponto central.

    Returns:
    - List[Tuple[float, float]]: Lista de coordenadas dos pontos ao redor.
    """
    points = []
    
    # Converter latitude e longitude de graus para radianos
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)
    
    # Raio da Terra em km
    R = 6371.0
    
    for i in range(num_points):
        # Calcular o ângulo de cada ponto
        angle = 2 * math.pi * i / num_points
        
        # Calcular a nova latitude
        new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(radius_km / R) +
                                math.cos(lat_rad) * math.sin(radius_km / R) * math.cos(angle))
        
        # Calcular a nova longitude
        new_lon_rad = lon_rad + math.atan2(math.sin(angle) * math.sin(radius_km / R) * math.cos(lat_rad),
                                           math.cos(radius_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad))
        
        # Converter de radianos para graus
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        
        points.append((new_lat, new_lon))

    return points
###########################################################################################################################
import gpxpy # pip install gpxpy
import gpxpy.gpx
###########################################################################################################################
def GerarGpx_com_Waypoints(RouteDetail,filename="waypoints.gpx"):
    # Criar um objeto GPX
    gpx = gpxpy.gpx.GPX()

    #waypoints = []
    #for wp in RouteDetail.waypnts:
        # print(f"Nome: {wp.street}, Latitude: {wp.lat}, Longitude: {wp.lon}")
    #    waypoints.append({'name': wp.street, 'lat': wp.lat, 'lon': wp.lon})
        
    # Criar três waypoints com coordenadas diferentes
    # waypoints = [
    #    {'name': 'Waypoint 1', 'lat': -22.87017, 'lon': -43.16546},
    #    {'name': 'Waypoint 2', 'lat': -22.86967, 'lon': -43.17104},
    #    {'name': 'Waypoint 3', 'lat': -22.8684,  'lon': -43.18506}
    # ]
    
    # Adicionar os waypoints ao GPX
    for wp in RouteDetail.waypnts:
        waypoint = gpxpy.gpx.GPXWaypoint(latitude= wp.lat, longitude=wp.lon, name=wp.street)
        gpx.waypoints.append(waypoint)
    
    # Gerar o conteúdo do arquivo GPX
    gpx_data = gpx.to_xml()

    # Salvar o arquivo GPX
    with open(filename, 'w') as f:
        f.write(gpx_data)

    wLog(f"Arquivo {filename} gerado com sucesso!")
###########################################################################################################################    
def GerarGpx_com_Tracks(RouteDetail, nome_arquivo='track.gpx'):
    """
    Salva um arquivo GPX com uma lista de coordenadas.
    
    :param coordenadas: Lista de tuplas contendo (latitude, longitude, elevação)
    :param nome_arquivo: Nome do arquivo GPX de saída
    """
    # Cria um objeto GPX
    gpx = gpxpy.gpx.GPX()

    # Cria uma nova trilha (track)
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Cria um novo segmento de trilha
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Adiciona as coordenadas fornecidas ao segmento da trilha
    for wp in RouteDetail.waypnts:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(wp.lat, wp.lon, elevation=0.0))

    # Salva o arquivo GPX
    with open(nome_arquivo, 'w') as f:
        f.write(gpx.to_xml())

    wLog(f"Arquivo GPX '{nome_arquivo}' criado com sucesso.")
################################################################################
import datetime
def TimeStringTmp():
    # Obtém a data e hora atuais
    agora = datetime.datetime.now()
    # Formata a data e hora em uma string no formato AAAA-MM-DD_HH-MM-SS
    buf = agora.strftime("%Y-%m-%d_%H-%M-%S")
    return buf    
################################################################################
from math import radians, sin, cos, sqrt, atan2
################################################################################
def calcular_distancia_haversine(ponto1, ponto2):
    """
    Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine.
    
    Args:
        ponto1 (list): Coordenadas [latitude, longitude] do ponto 1.
        ponto2 (list): Coordenadas [latitude, longitude] do ponto 2.
    
    Returns:
        float: Distância em quilômetros entre os dois pontos.
    """
    # Raio médio da Terra em quilômetros
    R = 6371.0

    # Coordenadas em radianos
    lat1, lon1 = radians(ponto1[0]), radians(ponto1[1])
    lat2, lon2 = radians(ponto2[0]), radians(ponto2[1])

    # Diferenças das coordenadas
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distancia = R * c

    return distancia
################################################################################
# Função para ordenar os pontos de visita, pelo ultimo mais próximo, segundo a chatgpt, algoritmo ganancioso... 
def OrdenarPontos(pontosvisita):
    ordenados = [pontosvisita.pop(0)]  # Iniciar a lista com o primeiro ponto
    while pontosvisita:
        ultimo_ponto = ordenados[-1]
        proximo_ponto = min(pontosvisita, key=lambda p: Haversine(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1]))
        ordenados.append(proximo_ponto)
        pontosvisita.remove(proximo_ponto)
    return ordenados
################################################################################
import os
import shutil
################################################################################
def GeraArquivoExclusoes(regioes, arquivo_saida="exclusion.poly"):
    """
    Gera um arquivo .poly a partir de uma lista de regiões.

    Args:
        regioes (list): Lista de regiões, onde cada região é um dicionário contendo:
                        - "nome" (str): Nome da região.
                        - "coord" (list): Lista de coordenadas [(latitude, longitude), ...].
        arquivo_saida (str): Nome do arquivo de saída.
    """
    wLog("GeraArquivoExclusoes")
    try:
        if os.path.exists(arquivo_saida):
           arquivo_backup = f"{arquivo_saida}.old"
           shutil.move(arquivo_saida, arquivo_backup)
        with open(arquivo_saida, "w") as f:
            f.write(f"AreasRoteamento\n")
            for regiao in regioes:
                nome = regiao.get("nome", "SemNome").replace(" ", "_")
                coordenadas = regiao.get("coord", [])
                
                # Escrever o nome da região no arquivo
                f.write(f"{nome}\n")
                wLog(f"Região adicionada: {nome}")
                
                # Escrever as coordenadas da região
                for i, (latitude, longitude) in enumerate(coordenadas):
                    f.write(f"   {longitude} {latitude}\n")
                
                # Encerrar a definição da região
                f.write("END\n")
            f.write("END\n")        
        wLog(f"Arquivo '{arquivo_saida}' gerado com sucesso.")
    
    except Exception as e:
        wLog(f"Erro ao gerar o arquivo .poly: {e}")
################################################################################
class ClUserData:
    def __init__(self):
        """
        Inicializa os dados do usuário.
        """
        self.nome = None
        self.OSMRport = None
        self.Regioes = None
        return
################################################################################
UserData = ClUserData()    
################################################################################
import socket
################################################################################
def FindFreePort(start_port=50000, max_port=65535):
    """
    Procura a primeira porta disponível no host local a partir de uma porta inicial.
    
    Args:
        start_port (int): Porta inicial para começar a busca.
        max_port (int): Número máximo de porta a verificar (default: 65535).
    
    Returns:
        int: O número da primeira porta disponível.
    
    Raises:
        RuntimeError: Se nenhuma porta estiver disponível no intervalo.
    """
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Tenta vincular o socket à porta
                s.bind(("localhost", port))
                return port  # Retorna a porta se estiver disponível
            except OSError:
                continue  # Porta está em uso, passa para a próxima
    raise RuntimeError(f"Nenhuma porta livre encontrada no intervalo {start_port}-{max_port}.")
################################################################################
import subprocess
import os
def FiltrarRegiãoComOsmosis():
    # Salvar o diretório atual
    diretorio_atual = os.getcwd()
    os.chdir("../../Osmosis")
    # Inicia e configura a máquina do Podman
    subprocess.run(["filter.bat",UserData.nome])
    os.chdir(diretorio_atual)
################################################################################
def SubstAcentos(texto):
    """
    Substitui caracteres acentuados por suas versões sem acento.
    """
    mapeamento = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'ç': 'c', 'Ç': 'C',
        'ñ': 'n', 'Ñ': 'N'
    }
    
    # Substitui cada caractere com base no mapeamento
    for acentuado, sem_acento in mapeamento.items():
        texto = texto.replace(acentuado, sem_acento)
    
    return texto
################################################################################
def wLog(log_string):
    log_file = f"{FileLog}.{UserData.nome}"  # Nome do arquivo de log
        
    timStp = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
    log_string = SubstAcentos(log_string)
    log_string = timStp+" : "+log_string
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(log_file):
            with open(log_file, "w") as file:
                file.write(timStp+" : "+"### Inicio do Log ###\n")  # Opcional: cabeçalho inicial
        # Abre o arquivo no modo append (adicionar)
        with open(log_file, "a") as file:
            file.write(log_string + "\n")  # Escreve a mensagem com uma nova linha
        print(log_string)  # Também exibe a mensagem no console
    except Exception as e:
        print(f"Erro ao escrever no log: {e}")    
################################################################################  
def AtivaServidorOSMR():
    # startserver filtro 8001 osmr_server8001
    StopOldContainers(days=30)
    diretorio_atual = os.getcwd() 
    os.chdir("../../OSMR/data")
    UserData.OSMRport =  FindFreePort(start_port=50000, max_port=65535)
    wLog(f"Porta tcp/ip disponivel encontrada: {UserData.OSMRport}")
    if FileLog=="":
        wLog("Ativando Servidor OSMR")
        subprocess.Popen(["StartServer.bat",str(UserData.OSMRport),UserData.nome],shell=True,creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        wLog(f"Ativando Servidor OSMR log {FileLog}.{UserData.nome}.OSMR")
        with open(FileLog+f".{UserData.nome}.OSMR", "w+", encoding="utf-8") as log_file:
            subprocess.Popen(["StartServer.bat",str(UserData.OSMRport),UserData.nome], stdout=log_file,stderr=log_file,creationflags=subprocess.CREATE_NO_WINDOW)     
    os.chdir(diretorio_atual)
    return
################################################################################
def GerarIndicesExecutarOSRMServer():
    # Salvar o diretório atual
    diretorio_atual = os.getcwd()
    os.chdir("../../OSMR/data")
    DeleteOldFilesAndFolders("TempData", days=30)
    subprocess.run(["GeraIndices.bat", UserData.nome])
    os.chdir(diretorio_atual)
    AtivaServidorOSMR()
    return
################################################################################
import subprocess
import datetime
################################################################################
def get_containers():
    """
    Obtém a lista de contêineres, incluindo o ID e a data de criação.
    Retorna uma lista de tuplas (container_id, created_at).
    """
    result = subprocess.run(
        ["podman", "ps", "-a", "--format", "{{.ID}} {{.CreatedAt}}"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print("Erro ao listar contêineres")
        return []

    containers = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        container_id, created_at = parts[0], parts[1]
        containers.append((container_id, created_at))
    return containers
################################################################################
def StopOldContainers(days=30):
    """
    Para contêineres que têm mais de 'days' dias de idade.
    """
    # Obtém a data atual
    current_time = datetime.datetime.now()

    # Obtém os contêineres
    containers = get_containers()

    for container_id, created_at in containers:
        # Converte a data de criação para um objeto datetime
        try:
            # Remover a parte extra do fuso horário (a última parte)
            created_at_cleaned = created_at.split(' ')[0] + ' ' + created_at.split(' ')[1]  # Remove a parte extra de fuso horário
            created_at_cleaned = created_at_cleaned[:26]
            # wLog("---------------------- Data com problema "+created_at_cleaned)
            created_time = datetime.datetime.strptime(created_at_cleaned,"%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # Caso o formato de data não tenha microsegundos
            created_at_cleaned = created_at.split(' ')[0] + ' ' + created_at.split(' ')[1]  # Remove a parte extra de fuso horário
            created_at_cleaned = created_at_cleaned[:26]
            # wLog("---------------------- Data ajustada "+created_at_cleaned)
            created_time = datetime.datetime.strptime(created_at_cleaned,"%Y-%m-%d %H:%M:%S.%f")
        
        # Calcula a diferença de dias entre a data atual e a data de criação
        age_in_days = (current_time - created_time).days
        # wLog(f"---------------------- age_in_days: {age_in_days}")
         
        # Se o contêiner for mais antigo que o limite (30 dias)
        if age_in_days > days:
            print(f"Parando contêiner {container_id} (idade: {age_in_days} dias)")
            subprocess.run(["podman", "stop", container_id])
################################################################################
import requests
import time
################################################################################
def VerificarOsrmAtivo(tentativas=100000, intervalo=5):
    """
    Verifica se o servidor OSRM está ativo.

    Args:
    - url: URL do serviço de rota OSRM.
    - tentativas: Número máximo de tentativas de verificação.
    - intervalo: Intervalo de tempo (em segundos) entre as tentativas.

    Returns:
    - bool: True se o servidor estiver no ar, False caso contrário.
    """
    url = f"http://localhost:{UserData.OSMRport}/route/v1/driving/-43.105772903105354,-22.90510838815471;-43.089637952126694,-22.917360518277434?overview=full&geometries=polyline&steps=true"

    for tentativa in range(tentativas):
        try:
            # Faz a requisição GET
            response = requests.get(url)
            
            # Verifica o código de status HTTP
            if response.status_code == 200:
                wLog("OSRM está funcionando corretamente.")
                return True
            else:
                wLog(f"Tentativa {tentativa + 1}/{tentativas}: Erro {response.status_code}. Tentando novamente...")
        
        except requests.exceptions.RequestException as e:
            wLog(f"Tentativa {tentativa + 1}/{tentativas}: Erro ao acessar o OSRM: {e}. Tentando novamente...")
        
        # Aguarda o intervalo antes de tentar novamente
        time.sleep(intervalo)
    
    wLog("O servidor OSRM não ficou disponível após várias tentativas.")
    return False
################################################################################
def VerificarServidorAtivo(url,reposta,tentativas=10, intervalo=1):
    """
    Verifica se o servidor url está ativo.

    Args:
    - url: URL a ser testada
    - tentativas: Número máximo de tentativas de verificação.
    - intervalo: Intervalo de tempo (em segundos) entre as tentativas.

    Returns:
    - bool: True se o servidor estiver no ar, False caso contrário.
    """

    for tentativa in range(tentativas):
        try:
            # Faz a requisição GET
            response = requests.get(url)
            # print(response.text)
            # Verifica o código de status HTTP
            if response.text == reposta:
                # print(f"Servidor OK.")
                return True
        
        except requests.exceptions.RequestException as e:
            pass
        
        # Aguarda o intervalo antes de tentar novamente
        time.sleep(intervalo)
    
    return False
################################################################################
FileLog="WebRotasServer.log"
################################################################################
def AtivaServidorWebRotas():
    teste=VerificarServidorAtivo("http://localhost:5001/ok","ok",tentativas=3, intervalo=1)
    if(not teste):
       if FileLog=="":
          subprocess.Popen(["start","startserver.bat"],shell=True,creationflags=subprocess.CREATE_NEW_CONSOLE)
          wLog("Ativando Servidor")
          return 
       else:
           wLog(f"Ativando Servidor log {FileLog}")
           with open(FileLog, "w+", encoding="utf-8") as log_file:
               subprocess.Popen(["startserver.bat"], stdout=log_file,stderr=log_file,creationflags=subprocess.CREATE_NO_WINDOW) 
           return 
    else:
        wLog("Servidor Ativo")       
    return
################################################################################
import psutil # pip install psutil
################################################################################
def KillProcessByCommand(target_command):
    """
    Encerra processos com base em um comando específico.

    :param target_command: Parte do comando que identifica o processo a ser encerrado (string).
    """
    found = False  # Para verificar se algum processo foi encontrado
    for process in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            # Obtém a linha de comando do processo
            cmdline = process.info["cmdline"]
            # Verifica se cmdline não é None e contém o comando alvo
            if cmdline and target_command in cmdline:
                wLog(f"Matando processo {process.info['name']} (PID: {process.info['pid']})")
                process.kill()  # Encerra o processo
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if not found:
        # wLog(f"Nenhum processo encontrado com o comando '{target_command}'.")
        pass
    else:
        # wLog("Processo encerrado com sucesso, se encontrado.")
        pass

################################################################################
def MataServidorWebRotas():
    KillProcessByCommand("Server.py")
    return
################################################################################
import subprocess
import sys
import os
import urllib.request
################################################################################
def verificar_podman_instalado():
    """Verifica se o Podman está instalado no Windows."""
    try:
        # Verifica se o podman está disponível no sistema
        result = subprocess.run(["podman", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            wLog("Podman já está instalado.")
            return True
        else:
            wLog("Podman não encontrado.")
            return False
    except FileNotFoundError:
        wLog("Podman não encontrado.")
        return False
################################################################################
def baixar_instalar_podman():
    """Baixa e instala o Podman no Windows usando o setup.exe."""
    # URL do instalador do Podman para Windows
    url = "https://github.com/containers/podman/releases/download/v5.3.1/podman-5.3.1-setup.exe"
    destino = "podman-setup.exe"

    wLog("Baixando o instalador do Podman...")
    # Baixa o arquivo setup.exe
    urllib.request.urlretrieve(url, destino)
    
    wLog("Instalando o Podman...")
    # Executa o instalador de forma silenciosa
    subprocess.run([destino, "/S"], check=True)
    
    # Verifica se a instalação foi bem-sucedida
    if verificar_podman_instalado():
        wLog("Podman foi instalado com sucesso!")
    
    # Remove o arquivo de instalação
    os.remove(destino)
################################################################################
def VerificaPodman():
    if not verificar_podman_instalado():
       baixar_instalar_podman()
################################################################################
import os
import filecmp
################################################################################
def VerificaArquivosIguais(arquivo_atual, arquivo_backup):
    # Verifica se ambos os arquivos existem
    if not os.path.exists(arquivo_atual):
        wLog(f"O arquivo atual '{arquivo_atual}' não existe.")
        return False
    if not os.path.exists(arquivo_backup):
        wLog(f"O arquivo backup '{arquivo_backup}' não existe.")
        return False

    # Compara os arquivos
    arquivos_sao_iguais = filecmp.cmp(arquivo_atual, arquivo_backup, shallow=False)
    return arquivos_sao_iguais
################################################################################
def PreparaServidorRoteamento(regioes):
    DeleteOldFilesAndFolders("logs", days=30)
    DeleteOldFilesAndFolders("../../Osmosis/TempData", days=30)
    GeraArquivoExclusoes(regioes, arquivo_saida=f"../../Osmosis/TempData/exclusion_{UserData.nome}.poly")
    if not VerificaArquivosIguais(f"../../Osmosis/TempData/exclusion_{UserData.nome}.poly", f"../../Osmosis/TempData/exclusion_{UserData.nome}.poly.old"):
       wLog("FiltrarRegiãoComOsmosis")  
       FiltrarRegiãoComOsmosis()       
       wLog("GerarIndicesExecutarOSRMServer")  
       GerarIndicesExecutarOSRMServer()
    else:
       wLog("Arquivo exclusoes nao modificado, nao e necessario executar osmisis") 
       AtivaServidorOSMR()
    VerificarOsrmAtivo()     
################################################################################    
def DesenhaRegioes(RouteDetail,regioes):  
    # Processa as regiões
    wLog("Plotando Regiões de mapeamento e exclusões")
    
    RegiaoExclusão = False 
    for regiao in regioes:
        nome = regiao.get("nome", "Sem Nome").replace(" ", "")
        if "!" in nome:
            nome = nome.replace("!", "")
            RegiaoExclusão = True
        else:
            RegiaoExclusão = False    
            
        RouteDetail.mapcode += f"    região{nome} = [\n"
        coordenadas = regiao.get("coord", [])
        wLog(f"  Região: {nome}")
        i=0
        for coord in coordenadas:
            latitude, longitude = coord
            if i == len(coordenadas) - 1:  # Verifica se é o último elemento
               RouteDetail.mapcode += f"       [{latitude}, {longitude}]\n"               
            else: 
               RouteDetail.mapcode += f"       [{latitude}, {longitude}]," 
            i=i+1   
        RouteDetail.mapcode += f"    ];\n"
        if(RegiaoExclusão):
           RouteDetail.mapcode += f"var polygon{nome} = L.polygon(região{nome}, {{ color: 'red',fillColor: 'lightred',fillOpacity: 0.2, weight: 1}}).addTo(map);\n"
        else:
           RouteDetail.mapcode += f"var polygon{nome} = L.polygon(região{nome}, {{ color: 'green',fillColor: 'lightgreen',fillOpacity: 0.0, weight: 1}}).addTo(map);\n"
    return RouteDetail          
################################################################################    
def DesenhaMunicipio(RouteDetail,nome,polMunicipio):         
    indPol=0
    for poligons in polMunicipio:
        i=0
        RouteDetail.mapcode += f"    municipio{nome}Pol{indPol} = [\n"
        for coordenada in poligons:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            longitude,latitude = coordenada
            if i == len(poligons) - 1:  # Verifica se é o último elemento
               RouteDetail.mapcode += f"       [{latitude}, {longitude}]]\n"               
            else: 
               RouteDetail.mapcode += f"       [{latitude}, {longitude}]," 
            i=i+1   
        RouteDetail.mapcode += f"var polygonMun{nome}{indPol} = L.polygon(municipio{nome}Pol{indPol}, {{ color: 'green',fillColor: 'lightgreen',fillOpacity: 0.0, weight: 1}}).addTo(map);\n"
        indPol=indPol+1
    return RouteDetail          
################################################################################
# zzzzzzzzzzzzz
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic    # pip install geopy
import numpy as np
################################################################################
def GeneratePointsWithinCity(city_boundary,regioes, distance):
    """
    Gera uma lista de pontos (lat, lon) distribuídos dentro da área delimitada por um polígono.

    :param city_boundary: Lista de coordenadas [(lat1, lon1), (lat2, lon2), ...] definindo o polígono da cidade.
    :param distance: Distância em metros entre os pontos.
    :return: Lista de pontos [(lat, lon)] dentro das fronteiras.
    """
    # Converter a lista de coordenadas em um polígono
    polygonsList = []
    for poligonsMun in city_boundary:
       polygonsList.append(Polygon([(float(lon), float(lat)) for lat, lon in poligonsMun]))  # Shapely usa (x, y)

    polAvoidList = []
    for regiao in regioes:
        nome = regiao.get("nome", "Sem Nome")
        if "!" in nome:
            coordenadas = regiao.get("coord", [])
            polAvoidList.append(Polygon([(float(lat), float(lon)) for lat, lon in coordenadas]))    

    # wLog("Coordenadas externas polygonsList[0]:")
    # for coord in polygonsList[0].exterior.coords:
    #    wLog(coord)    

    # wLog("Coordenadas externas polAvoidList[0]:")
    #for coord in polAvoidList[0].exterior.coords:
    #    wLog(coord)    
        
    # Obter os limites do polígono (bounding box)
    # min_lon, min_lat, max_lon, max_lat = polygon.bounds

    all_bounds = [polygon.bounds for polygon in polygonsList]
    min_lon = min(bound[0] for bound in all_bounds)  # xmin
    min_lat = min(bound[1] for bound in all_bounds)  # ymin
    max_lon = max(bound[2] for bound in all_bounds)  # xmax
    max_lat = max(bound[3] for bound in all_bounds)  # ymax

    # Função auxiliar para calcular o deslocamento em graus
    def meter_to_degree(base_point, distance_m):
        ref_point = (base_point[0] + 0.1, base_point[1])  # Um ponto próximo para calcular a relação
        degree_distance = geodesic(base_point, ref_point).meters / 0.1
        return float(distance_m) / float(degree_distance)

    # Calcular passos em latitude e longitude
    lat_step = meter_to_degree((min_lat, min_lon), distance)
    lon_step = meter_to_degree((min_lat, min_lon), distance)

    # Gerar uma grade de pontos
    lat_range = np.arange(min_lat, max_lat, lat_step)
    lon_range = np.arange(min_lon, max_lon, lon_step)

    # Filtrar pontos dentro do polígono
    points_within_city = []
    for lat in lat_range:
        for lon in lon_range:
            point = Point(lon, lat)
            for polygon in polygonsList:
                if polygon.contains(point):
                    insideAvoidRegion=0 
                    for polygonAvoid in polAvoidList: 
                        if polygonAvoid.contains(point):
                           insideAvoidRegion=1 
                    if(insideAvoidRegion==0):       
                        points_within_city.append((lon, lat))

    return points_within_city
################################################################################
# Exemplo de uso
# city_boundary = [
#     (-23.5505, -46.6333),  # São Paulo exemplo
#     (-23.5485, -46.6340),
#     (-23.5470, -46.6300),
#     (-23.5500, -46.6280),
#     (-23.5505, -46.6333)   # Fechando o polígono
# ]

# distance_between_points = 100  # Distância entre pontos em metros
# points = generate_points_within_city(city_boundary, distance_between_points)
# print(f"Número de pontos gerados: {len(points)}")
# print(points[:10])  # Mostra os primeiros 10 pontos gerados
################################################################################
def ServerSetupJavaScript(RouteDetail):
    if ServerTec == "OSMR":
       RouteDetail.mapcode += f"    const ServerTec = 'OSMR';\n"
       RouteDetail.mapcode += f"    const OSRMPort = {UserData.OSMRport};\n"
    if ServerTec == "GHopper":
       RouteDetail.mapcode += f"    const ServerTec = 'GHopper';\n"
    return RouteDetail
################################################################################
def RouteCompAbrangencia(user,cidade,uf,distanciaPontos,regioes):
    
    UserData.nome=user
    PreparaServidorRoteamento(regioes)
    RouteDetail = ClRouteDetailList()
    

    RouteDetail = ServerSetupJavaScript(RouteDetail)   
       
    RouteDetail.mapcode += f"    const TipoRoute = 'CompAbrangencia';\n"   
    
    polMunicipio= GetBoundMunicipio(cidade, uf)
    # print("Depurando polMunicipio")
    # print(polMunicipio)
    RouteDetail = DesenhaMunicipio(RouteDetail,cidade,polMunicipio)
    
    wLog("Ordenando e processando Pontos de Visita:")
    pontosvisita = GeneratePointsWithinCity(polMunicipio, regioes, distanciaPontos)
    pontosvisita = OrdenarPontos(pontosvisita) 
    RouteDetail = PlotaPontosVisita(RouteDetail,pontosvisita)
    
    RouteDetail=DesenhaRegioes(RouteDetail,regioes)
    RouteDetail.GeraMapPolylineCaminho()
          
    buf = TimeStringTmp()   
    fileMap = f"MapaCompAbrangencia{buf}.html"     
    fileName = f"templates/{fileMap}"
    gm.GeraMapaLeaflet(fileName,RouteDetail)

    return fileMap
################################################################################
def PlotaPontosVisita(RouteDetail,pontosvisita):
    wLog("PlotaPontosVisita")
    i=0
    RouteDetail.mapcode += f"    pontosVisita = [\n"
    for ponto in pontosvisita:
        latitude, longitude = ponto
        if i == len(pontosvisita) - 1:  # Verifica se é o último elemento
           RouteDetail.mapcode += f"       [{latitude}, {longitude}]"
        else: 
           RouteDetail.mapcode += f"       [{latitude}, {longitude}]," 
           
        # print(f"  Latitude: {latitude}, Longitude: {longitude}")
    RouteDetail.mapcode += f"    ];\n"
    
    # Criar um mapa  
    # RouteDetail.mapcode += f"    const map = L.map('map');\n"
    RouteDetail.mapcode += f"    map.fitBounds(L.latLngBounds(pontosVisita));\n"        
 
    i=0
    RouteDetail.mapcode += "var markerVet = [];";
    for ponto in pontosvisita:
        lat, lon = ponto
        RouteDetail.mapcode += f"         markerbufTemp = L.marker([{lat}, {lon}]).addTo(map).on('click', onMarkerClick).setIcon(createSvgIcon({i}));\n"   
        RouteDetail.mapcode += f"         markerbufTemp._icon.setAttribute('data-id', '{i}'); markerbufTemp._icon.setAttribute('clicado', '0');\n"   
        RouteDetail.mapcode += f"         markerVet.push(markerbufTemp);\n"   
        if(i==0):
           (latfI,lonfI) = pontosvisita[i] 
        if(i==(len(pontosvisita) -1)):
           (latfF,lonfF) = pontosvisita[i]            
        if(i>0):
            (lati,loni) = pontosvisita[i-1]
            (latf,lonf) = pontosvisita[i]       
            RouteDetail=GenerateRouteMap(RouteDetail,lati,loni,latf,lonf)
        i=i+1    

    RouteDetail.mapcode +="           const defaultIcon = markerVet[1].getIcon();\n"      
    return RouteDetail
################################################################################
def RoutePontosVisita(user,pontosvisita,regioes):
    
    UserData.nome=user
    PreparaServidorRoteamento(regioes)
    RouteDetail = ClRouteDetailList()
           
    RouteDetail = ServerSetupJavaScript(RouteDetail)     
    RouteDetail.mapcode += f"    const TipoRoute = 'PontosVisita';\n"   
    
    # Criar um mapa centrado no ponto central
    # RouteDetail.mapcode += f"    const map = L.map('map').setView(13);\n"
    
    # Processa Pontos de Visita
    wLog("Ordenando e processando Pontos de Visita:")
    pontosvisita=OrdenarPontos(pontosvisita) 
    RouteDetail = PlotaPontosVisita(RouteDetail,pontosvisita)
    RouteDetail=DesenhaRegioes(RouteDetail,regioes)
    RouteDetail.GeraMapPolylineCaminho()
    # GerarKml(coordenadasrota, filename="rota.kml")
    
    # servidor temp     python3 -m http.server 8080
    #           
    buf = TimeStringTmp()   
    fileMap = f"MapaPontosVisita{buf}.html"     
    fileName = f"templates/{fileMap}"
    gm.GeraMapaLeaflet(fileName,RouteDetail)

    return fileMap
###########################################################################################################################
def RouteDriveTest(user,central_point,regioes,radius_km=5):
    # Coordenadas do ponto central (latitude, longitude)
    # central_point = [40.712776, -74.005974]  # Exemplo: Nova York
    #central_point = [-22.90941986104239, -43.16486081793237] # Santos Dumont
    # central_point = [-22.891147608655164, -43.05261174054559] #   Niteroi IFR
    # central_point = [-21.701103198880247, -41.308194753766394] #   Aeroporto de Campos
 
    #central_point = [-22.9864182585604, -43.37041245345915] 
    
    UserData.nome=user
    PreparaServidorRoteamento(regioes)
    
    RouteDetail = ClRouteDetailList()
    
    RouteDetail = ServerSetupJavaScript(RouteDetail)  
    
    RouteDetail.mapcode += f"    const TipoRoute = 'DriveTest';\n"
    
    # Criar um mapa centrado no ponto central
    # RouteDetail.mapcode += f"    const map = L.map('map').setView([{central_point[0]}, {central_point[1]}], 13);\n"
    RouteDetail.mapcode += f"     map.setView([{central_point[0]}, {central_point[1]}], 13);\n"
    
    # Adicionar uma marca no ponto central
    RouteDetail.mapcode += f"    var markerCentral = L.marker([{central_point[0]}, {central_point[1]}]).addTo(map).bindPopup('Ponto Central'); \n"
    RouteDetail.mapcode += "     markerCentral.setIcon(iMarquerVerde);\n"
    # Coordenadas da rota (exemplo de uma rota circular simples)   
    num_points=8
    route_coords = GeneratePointsAround(latitude=central_point[0], longitude=central_point[1], radius_km=radius_km, num_points=num_points)

    # Adicionar a rota no mapa
    RouteDetail.mapcode += "var markerVet = [];";
    for i, (lat, lon) in enumerate(route_coords):
        RouteDetail.mapcode += f"         markerVet.push(L.marker([{lat}, {lon}]).addTo(map).on('click', onMarkerClick).setIcon(createSvgIcon({i})));\n"             
         
        # RouteDetail.mapcode += f"         markerVet.push(L.marker([{lat}, {lon}]).addTo(map).on('click', onMarkerClick).setIcon(iMarquerAzul).bindPopup('P{i}'));\n"             
        if(i==0):
           (latfI,lonfI) = route_coords[i] 
        if(i==(num_points-1)):
           (latfF,lonfF) = route_coords[i]            
        if(i>0):
            (lati,loni) = route_coords[i-1]
            (latf,lonf) = route_coords[i]       
            RouteDetail=GenerateRouteMap(RouteDetail,lati,loni,latf,lonf)
    RouteDetail.mapcode +="           const defaultIcon = markerVet[1].getIcon();"        
    # map,RouteDetail=GenerateRouteMap(map,RouteDetail,latfI,lonfI,latfF,lonfF) # retorno ao ponto inicial
 
    RouteDetail=DesenhaRegioes(RouteDetail,regioes)
    RouteDetail.GeraMapPolylineCaminho()
    # GerarKml(coordenadasrota, filename="rota.kml")
    
    # servidor temp     python3 -m http.server 8080
    #           
    buf = TimeStringTmp()   
    fileMap = f"MapaDriveTest{buf}.html"     
    fileName = f"templates/{fileMap}"
    gm.GeraMapaLeaflet(fileName,RouteDetail)

    return fileMap
###########################################################################################################################
def main():
    # Coordenadas do ponto central (latitude, longitude)
    # central_point = [40.712776, -74.005974]  # Exemplo: Nova York
    # central_point = [-22.90941986104239, -43.16486081793237] # Santos Dumont
    central_point = [-22.891147608655164, -43.05261174054559] #   Niteroi IFR
    # central_point = [-21.701103198880247, -41.308194753766394] #   Aeroporto de Campos
 
    #central_point = [-22.9864182585604, -43.37041245345915] 
    
    RouteDriveTest(central_point,radius_km=5)
    return
###########################################################################################################################
if __name__ == "__main__":
    main()
###########################################################################################################################    
