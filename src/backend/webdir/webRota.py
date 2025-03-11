###########################################################################################################################
import geraMapa as gm
import shapeFiles as sf

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

# conda create --name webrotas python=3.11
# conda activate webrotas

###########################################################################################################################
class ClRouteDetailList:
    def __init__(self):
        self.list = []
        self.ind=0    
        self.coordinates = []
        self.pontosvisitaDados = []
        self.mapcode = ""   
        self.pontoinicial = None    
        self.DistanceTotal = 0

    #---------------------------------------------------
    def GeraMapPolylineCaminho(self):
        wLog("Plotando polyline rota")
        self.mapcode += "\n"
                  
        self.mapcode += """var polylineRotaDat = ["""     
        for ind,poliLine in enumerate(self.coordinates):  
            self.mapcode += """["""  
            for i, (lat, lon) in enumerate(poliLine):
                if i == len(poliLine) - 1:  # Último elemento
                    self.mapcode += f"[{lat}, {lon}]"
                else:
                    self.mapcode += f"[{lat}, {lon}], "
            if ind == len(self.coordinates) - 1:  # Último elemento        
                self.mapcode += """]"""
            else:
                self.mapcode += """],"""    
        self.mapcode += """];"""
                
        self.mapcode += """
           poly_lineRota = [];
           for (let i = 0; i < polylineRotaDat.length; i++) 
           {            
                var tempBuf = L.polyline(polylineRotaDat[i], {
                "bubblingMouseEvents": true,"color": "blue","dashArray": null,"dashOffset": null,
                "fill": false,"fillColor": "blue","fillOpacity": 0.2,"fillRule": "evenodd","lineCap": "round",
                "lineJoin": "round","noClip": false,"opacity": 0.7,"smoothFactor": 1.0,"stroke": true,
                "weight": 3}).addTo(map);\n
                 poly_lineRota.push(tempBuf);    
           }
           ListaRotasCalculadas[0].polylineRotaDat = polylineRotaDat;    
        """                          
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
import numpy as np
###########################################################################################################################    
def getElevationOpenElev(latitude, longitude):
    """
    Obtém a elevação de uma localização usando a API Open-Elevation.

    Args:
        latitude (float): Latitude da localização.
        longitude (float): Longitude da localização.

    Returns:
        float: Elevação em metros. Retorna 0 em caso de erro.
       
        Anatel, precisa login implementado em python
        fiscalizacao.anatel.gov.br/api/v1/lookup?locations=-22.919802062945383,-43.043920503331314
         
        Anatel, logado na vpn  
        http://rhfisnspdex02.anatel.gov.br/api/v1/lookup?locations=-22.919802062945383,-43.043920503331314
         
        Servidor free web 
        api.open-elevation.com/api/v1/lookup?locations=-22.919802062945383,-43.043920503331314  
        
    """
    url = "https://api.open-elevation.com/api/v1/lookup"
    urlVpn = "http://rhfisnspdex02.anatel.gov.br/api/v1/lookup"
    params = {
        "locations": f"{latitude},{longitude}"
    }

    def fetch_elevation(url):
        try:
            # Faz a requisição à API
            response = requests.get(url, params=params, timeout=10)  # Timeout de 10 segundos

            # Verifica se a requisição foi bem-sucedida
            response.raise_for_status()

            # Tenta decodificar o JSON da resposta
            data = response.json()

            # Verifica se a resposta contém os dados esperados
            if "results" in data and len(data["results"]) > 0:
                return round(data['results'][0]['elevation'])
            else:
                wLog("getElevationOpenElev Erro: Resposta da API não contém dados válidos.")
                return 0

        except requests.exceptions.RequestException as e:
            # Captura erros relacionados à requisição (conexão, timeout, etc.)
            print(f"getElevationOpenElev Erro na requisição: {e}")
            raise  # Re-lança a exceção para ser capturada no bloco externo

        except ValueError as e:
            # Captura erros de decodificação JSON
            print(f"getElevationOpenElev Erro ao decodificar JSON: {e}")
            return 0

        except KeyError as e:
            # Captura erros de chave ausente no JSON
            print(f"getElevationOpenElev Erro no formato da resposta: {e}")
            return 0

    try:
        return fetch_elevation(url)
    except requests.exceptions.RequestException:
        # Se a requisição à URL principal falhar, tenta a URL alternativa
        print("Tentando URL alternativa (VPN)...")
        return fetch_elevation(urlVpn)
###########################################################################################################################    
def getElevationOpenElevBatch(lat_lons, batch_size):
    """
    Obtém a elevação de múltiplas localizações usando a API Open-Elevation em lotes de 100.
    
    Args:
        lat_lons (list): Lista de tuplas contendo latitude e longitude.
        batch_size (int): Tamanho do lote para processamento.
    
    Returns:
        list: Lista de elevações em metros. Retorna 0 para coordenadas com erro.
        
        fiscalizacao.anatel.gov.br/api/v1/lookup?locations=-22.919802062945383,-43.043920503331314
        ou
        api.open-elevation.com/api/v1/lookup?locations=-22.919802062945383,-43.043920503331314
    """
    url = "https://api.open-elevation.com/api/v1/lookup"
    urlVpn = "http://rhfisnspdex02.anatel.gov.br/api/v1/lookup"
    elevations = []
    
    def fetch_batch_elevations(url, batch):
        """Função interna para buscar elevações de um lote."""
        locations = "|".join([f"{lat},{lon}" for lat, lon in batch])
        params = {"locations": locations}
        zbuf = url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
        
        wLog(f"---------------------------------------------------------") 
        wLog(f"getElevationOpenElevBatch URL da requisição: {zbuf}")  # Imprime a URL para depuração
        wLog(f"Tamanho do lote: {len(batch)}")
        wLog(f"---------------------------------------------------------") 
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                return [round(res["elevation"]) for res in data["results"]]
            else:
                wLog("getElevationOpenElevBatch Erro: Resposta da API não contém dados válidos.")
                return [0] * len(batch)
        
        except requests.exceptions.RequestException as e:
            wLog(f"getElevationOpenElevBatch Erro na requisição: {e}")
            raise  # Re-lança a exceção para ser capturada no bloco externo
        except ValueError as e:
            wLog(f"getElevationOpenElevBatch Erro ao decodificar JSON: {e}")
            return [0] * len(batch)
        except KeyError as e:
            wLog(f"getElevationOpenElevBatch Erro no formato da resposta: {e}")
            return [0] * len(batch)
    
    for i in range(0, len(lat_lons), batch_size):
        batch = lat_lons[i:i + batch_size]
        try:
            # Tenta a URL principal primeiro
            elevations.extend(fetch_batch_elevations(url, batch))
        except requests.exceptions.RequestException:
            # Se a URL principal falhar, tenta a URL alternativa
            wLog("Tentando URL alternativa (VPN)...")
            elevations.extend(fetch_batch_elevations(urlVpn, batch))
    
    return elevations  
###########################################################################################################################    
MinAltitude=50000 # Valor alto para garantir que a primeira altitude seja menor
MaxAltitude=0
###########################################################################################################################
def ResetAltitudes():
    global MinAltitude
    global MaxAltitude
    MinAltitude=50000
    MaxAltitude=0
    return
###########################################################################################################################
def AltitudeOpenElevation(latitude, longitude):
    
    global MinAltitude
    global MaxAltitude
    altitude = getElevationOpenElev(latitude, longitude)
    
    # Atualiza a altitude máxima
    if altitude > MaxAltitude:
        MaxAltitude = altitude

    # Atualiza a altitude mínima
    if altitude < MinAltitude:
        MinAltitude = altitude    
    
    return altitude
###########################################################################################################################
def AltitudeOpenElevationBatch(batch,batch_size):
    global MinAltitude
    global MaxAltitude
    ResetAltitudes()
    lat_lons = [(p[0], p[1]) for p in batch]
    altitudes = getElevationOpenElevBatch(lat_lons,batch_size)
    if altitudes:  # Verifica se a lista não está vazia
        MinAltitude = min(MinAltitude, min(altitudes)) 
        MaxAltitude = max(MaxAltitude, max(altitudes))   
        MinAltitude = int(MinAltitude) 
        MaxAltitude = int(MaxAltitude)  
    return altitudes    
###########################################################################################################################
import numpy as np
###########################################################################################################################
import os
###########################################################################################################################
import datetime
###########################################################################################################################
def Gerar_Kml(polyline_rota, pontos_visita_dados, filename="rota.kml"):
    # Cabeçalho do KML
    kml_inicio = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Pontos e Rotas</name>
    <!-- Definir estilos -->
    <Style id="lineStyleBlue">
      <LineStyle>
        <color>ff00ff00</color> <!-- verde em formato ABGR -->
        <width>4</width>
      </LineStyle>
    </Style>
"""

    # Footer do KML
    kml_fim = """
  </Document>
</kml>"""

    # Adicionar os pontos de visita
    kml_pontos = ""
    for latitude, longitude, id_ponto, tipo, descricao, altitude in pontos_visita_dados:
        kml_pontos += f"""
    <Placemark>
      <name>{id_ponto}</name>
      <description>{descricao}</description>
      <Point>
        <coordinates>{longitude},{latitude},{altitude}</coordinates>
      </Point>
    </Placemark>"""

    # Adicionar a polilinha (rota)
    kml_polyline=""    
    for ind,polyLineTmp in enumerate(polyline_rota): 
        kml_polyline += f"""
        <Placemark>
        <name>Rota{ind}</name>
        <styleUrl>#lineStyleBlue</styleUrl>
        <LineString>
            <coordinates>
        """
        for latitude, longitude in polyLineTmp:
            kml_polyline += f"          {longitude},{latitude},0\n"
        kml_polyline += """
            </coordinates>
        </LineString>
        </Placemark>"""

    # Combinar todas as partes
    kml_conteudo = kml_inicio + kml_pontos + kml_polyline + kml_fim

    with open(filename, "w", encoding="utf-8") as file:
        file.write(kml_conteudo)

    print(f"Arquivo KML '{filename}' gerado com sucesso!")

###########################################################################################################################
ServerTec = "OSMR"
###########################################################################################################################
def GetRouteFromServer(start_lat, start_lon, end_lat, end_lon):
   # 
   # Coordenadas de início e fim   
   start_coords = (start_lat, start_lon)
   end_coords = (end_lat, end_lon)
   
   if ServerTec == "OSMR":
      # URL da solicitação ao servidor OSRM
      url = f"http://localhost:{UserData.OSMRport}/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline&steps=true"
   
   wLog(url)
   # Fazer a solicitação
   response = requests.get(url)   
   return response
###########################################################################################################################
import os
import time
from datetime import datetime
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
    return RouteDetailLoc
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
       RouteDetailLoc.coordinates.append(coordinates)
       RouteDetailLoc.DistanceTotal = RouteDetailLoc.DistanceTotal + calcular_distancia_totalOSMR(data)            
    else:
       wLog(f"Erro na solicitação: {data}")    
       return RouteDetailLoc
            
    return RouteDetailLoc
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
import datetime
def TimeStringTmp():
    # Obtém a data e hora atuais
    agora = datetime.datetime.now()
    # Formata a data e hora em uma string no formato AAAA-MM-DD_HH-MM-SS
    buf = agora.strftime("%Y-%m-%d_%H-%M-%S")
    return buf    
################################################################################
import numpy as np
################################################################################
# Função para ordenar os pontos de visita, pelo ultimo mais próximo, segundo a chatgpt, algoritmo ganancioso... 
def OrdenarPontos(pontosvisita,pontoinicial):  
    # BenchmarkRotas(pontosvisita,pontoinicial)
    wLog(f"    Algoritmo: [{UserData.AlgoritmoOrdenacaoPontos}]")
    if UserData.AlgoritmoOrdenacaoPontos=="DistanciaGeodesica":     # "DistanciaOSMR", "DistanciaGeodesica", "DistanciaOSMRMultiThread"
       return OrdenarPontosDistanciaGeodesica(pontosvisita,pontoinicial)
    if UserData.AlgoritmoOrdenacaoPontos=="DistanciaOSMR":      
       return OrdenarPontosDistanciaOSMR(pontosvisita,pontoinicial)
    if UserData.AlgoritmoOrdenacaoPontos=="DistanciaOSMRMultiThread":      
       return OrdenarPontosDistanciaOSMRMultiThread(pontosvisita,pontoinicial)    
    return pontosvisita # Nenhuma seleção, não ordena os pontos
################################################################################
from concurrent.futures import ThreadPoolExecutor
import threading
################################################################################
# Função paralela para calcular a menor distância
def calcular_menor_distanciaThread(pontosvisita, ultimo_ponto):
    with ThreadPoolExecutor() as executor:
        distancias = executor.map(lambda p: (p, DistanciaRota(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1])), pontosvisita)
        return min(distancias, key=lambda x: x[1])[0]  # Retorna o ponto com menor distância
################################################################################
def OrdenarPontosDistanciaOSMRMultiThread(pontosvisita, pontoinicial):
    ordenados = [(pontoinicial[0], pontoinicial[1])]  # Iniciar a lista com o ponto inicial
    pontosvisita_lock = threading.Lock()

    while pontosvisita:
        ultimo_ponto = ordenados[-1]

        # Calcular o próximo ponto mais próximo em paralelo
        with pontosvisita_lock:  # Protege a lista durante a iteração
            proximo_ponto = calcular_menor_distanciaThread(pontosvisita, ultimo_ponto)
            ordenados.append(proximo_ponto)
            pontosvisita.remove(proximo_ponto)

    del ordenados[0]  # Remove o primeiro elemento, usado apenas como referência inicial da ordenação
    return ordenados

################################################################################
def calcular_distancia_totalOSMR(osmr_saida):
    """
    Calcula a distância total de uma rota com base nos passos fornecidos na saída do OSMR.
    
    :param osmr_saida: Dicionário contendo a saída do OSMR.
    :return: Distância total da rota em metros.
    """
    distancia_total = 0

    if "routes" in osmr_saida and osmr_saida["routes"]:
        for leg in osmr_saida["routes"][0]["legs"]:
            for step in leg["steps"]:
                distancia_total += step["distance"]
                
    return distancia_total
################################################################################
def DistanciaRota(start_lat, start_lon, end_lat, end_lon):
    response = GetRouteFromServer(start_lat, start_lon, end_lat, end_lon)
    data = response.json()
    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200 and 'routes' in data:
       return calcular_distancia_totalOSMR(data)
    else:
       wLog("DistanciaRota - erro pegando rota OSMR") 
       quit()       
    return 0
################################################################################
def DistanciaRotaTotal(pontosvisita):
    i=0
    dist=0
    for i in range(len(pontosvisita) - 1):
        dist += DistanciaRota(pontosvisita[i][0], pontosvisita[i][1], pontosvisita[i+1][0], pontosvisita[i+1][1])
        i=i+1
    return dist
################################################################################
# Função para ordenar os pontos de visita, metrica OSMR, pelo ultimo mais próximo, algoritmo ganancioso.
def OrdenarPontosDistanciaOSMR(pontosvisita,pontoinicial):
    ordenados = [(pontoinicial[0],pontoinicial[1])]  # Iniciar a lista com o ponto inicial
    while pontosvisita:
        ultimo_ponto = ordenados[-1]  # Obtém o último ponto adicionado à lista 'ordenados'
        proximo_ponto = min(pontosvisita, key=lambda p: DistanciaRota(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1]))
        ordenados.append(proximo_ponto)
        pontosvisita.remove(proximo_ponto)
    del ordenados[0]  # Remove o primeiro elemento, usado apenas como referência de inicial da ordenação    
    return ordenados
################################################################################
# Função para ordenar os pontos de visita, metrica Distâcia Geodesica , pelo ultimo mais próximo, algoritmo ganancioso.
def OrdenarPontosDistanciaGeodesica(pontosvisita,pontoinicial):
    ordenados = [(pontoinicial[0],pontoinicial[1])]  # Iniciar a lista com o ponto inicial
    while pontosvisita:
        ultimo_ponto = ordenados[-1]
        proximo_ponto = min(pontosvisita, key=lambda p: Haversine(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1]))
        ordenados.append(proximo_ponto)
        pontosvisita.remove(proximo_ponto)
    del ordenados[0]  # Remove o primeiro elemento, usado apenas como referência de inicial da ordenação    
    return ordenados
################################################################################
import time
################################################################################
def CronometraFuncao(func, *args, **kwargs):
    """
    Mede o tempo de execução de uma função.

    Parâmetros:
    - func: A função a ser cronometrada.
    - *args: Argumentos posicionais para a função.
    - **kwargs: Argumentos nomeados para a função.

    Retorna:
    - O resultado da função executada.
    - O tempo de execução em segundos.
    """
    try:
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time()
        tempo_execucao = fim - inicio
        return resultado, tempo_execucao
    except Exception as e:
        print(f"Erro ao executar a função: {e}")
        return None, None
################################################################################
def formatar_tempo(tempo_em_segundos):
    """
    Formata o tempo em minutos, segundos e milissegundos.

    Parâmetros:
    - tempo_em_segundos (float): Tempo em segundos.

    Retorna:
    - str: Tempo formatado como 'MM:SS:mmm'.
    """
    minutos, segundos = divmod(tempo_em_segundos, 60)
    segundos, milissegundos = divmod(segundos * 1000, 1000)
    return f"{int(minutos):02}:{int(segundos):02}:{int(milissegundos):03}"
################################################################################
def BenchmarkRotas(pontosvisita,pontoinicial):
    # 2024-12-28 23:11:33 : ---------------------------------------------------------------------------------------------
    # 2024-12-28 23:11:33 : BenchmarkRotas
    # 2024-12-28 23:34:42 : Tempo ordenacao geodesica: 00:00:001 minutos - Distancia rota: 250 km
    # 2024-12-28 23:34:42 : Tempo ordenacao OSMR: 17:56:159 minutos - Distancia rota: 158 km
    # 2024-12-28 23:34:42 : Tempo ordenacao OSMR MultiThread: 02:03:077 minutos - Distancia rota: 158 km
    # 2024-12-28 23:34:42 : ---------------------------------------------------------------------------------------------
    
    wLog("---------------------------------------------------------------------------------------------")
    wLog("BenchmarkRotas")
    #---------------------------------------
    pontosvisitaBench = pontosvisita.copy()
    pontosvisitaBench,tempoGeo = CronometraFuncao(OrdenarPontosDistanciaGeodesica,pontosvisitaBench,pontoinicial)
    tempoGeo = formatar_tempo(tempoGeo)
    distGeo = int(DistanciaRotaTotal(pontosvisitaBench)/1000)
    #---------------------------------------
    pontosvisitaBench = pontosvisita.copy()
    pontosvisitaBench,tempoOsmr = CronometraFuncao(OrdenarPontosDistanciaOSMR,pontosvisitaBench,pontoinicial)
    tempoOsmr = formatar_tempo(tempoOsmr)
    distOsmr = int(DistanciaRotaTotal(pontosvisitaBench)/1000)
    #---------------------------------------
    pontosvisitaBench = pontosvisita.copy()
    pontosvisitaBench,tempoOsmrThr = CronometraFuncao(OrdenarPontosDistanciaOSMRMultiThread,pontosvisitaBench,pontoinicial)
    tempoOsmrThr = formatar_tempo(tempoOsmrThr)
    distOsmrThr = int(DistanciaRotaTotal(pontosvisitaBench)/1000)    
    #---------------------------------------
    wLog(f"Tempo ordenação geodesica: {tempoGeo} minutos - Distancia rota: {distGeo} km")
    wLog(f"Tempo ordenação OSMR: {tempoOsmr} minutos - Distancia rota: {distOsmr} km")
    wLog(f"Tempo ordenação OSMR MultiThread: {tempoOsmrThr} minutos - Distancia rota: {distOsmrThr} km")
    wLog("---------------------------------------------------------------------------------------------")
    return
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
        self.AlgoritmoOrdenacaoPontos = None
        self.RaioDaEstacao = None
        self.GpsProximoPonto = None     
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
    os.chdir("../../resources/Osmosis")
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
    os.chdir("../../resources/OSMR/data")
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
    os.chdir("../../resources/OSMR/data")
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
def VerificarOsrmAtivo(tentativas=1000, intervalo=5):
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
    DeleteOldFilesAndFolders("../../resources/Osmosis/TempData", days=30)
    GeraArquivoExclusoes(regioes, arquivo_saida=f"../../resources/Osmosis/TempData/exclusion_{UserData.nome}.poly")
    if not VerificaArquivosIguais(f"../../resources/Osmosis/TempData/exclusion_{UserData.nome}.poly", f"../../resources/Osmosis/TempData/exclusion_{UserData.nome}.poly.old"):
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
    nome=SubstAcentos(nome).replace(" ", "_")
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
def DesenhaMunicipioAreasUrbanizadas(RouteDetail,nome,polMunicipioAreas):         
    indPol=0
    nome=SubstAcentos(nome).replace(" ", "_")
    for poligons in polMunicipioAreas:
        i=0
        RouteDetail.mapcode += f"    municipioAreasUrbanizadas{nome}Pol{indPol} = [\n"
        for coordenada in poligons:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            longitude,latitude = coordenada
            if i == len(poligons) - 1:  # Verifica se é o último elemento
               RouteDetail.mapcode += f"       [{latitude}, {longitude}]]\n"               
            else: 
               RouteDetail.mapcode += f"       [{latitude}, {longitude}]," 
            i=i+1   
        RouteDetail.mapcode += f"var polygonMunAreasUrbanizadas{nome}{indPol} = L.polygon(municipioAreasUrbanizadas{nome}Pol{indPol}, {{ color: 'rgb(74, 73, 73)',fillColor: 'lightblue',fillOpacity: 0.0, weight: 1, dashArray: '4, 4'}}).addTo(map);\n"
        indPol=indPol+1
    return RouteDetail         
################################################################################
# 
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
def ServerSetupJavaScript(RouteDetail):
    if ServerTec == "OSMR":
       RouteDetail.mapcode += f"    const ServerTec = 'OSMR';\n"
       RouteDetail.mapcode += f"    const OSRMPort = {UserData.OSMRport};\n"
    return RouteDetail
################################################################################
def DesenhaComunidades(RouteDetail,regioes):
    for regiao in regioes:
        nome = regiao.get("nome", "")
        if nome == "regiaoBoundingbox":
           coords = regiao.get("coord", [])
           lon_min = coords[0][1] 
           lat_min = coords[2][0]  
           lon_max = coords[1][1]   
           lat_max = coords[0][0]  
           break;
    bounding_box = (lon_min, lat_min, lon_max, lat_max)
    polylinesComunidades=sf.FiltrarComunidadesBoundingBox(bounding_box)       
    
    RouteDetail.mapcode += f"listComunidades = [\n"
    indPol=0
    for polyline in polylinesComunidades:
        i=0
        RouteDetail.mapcode += f"[\n"
        for coordenada in polyline:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            lat,lon = coordenada
            if i == len(polyline) - 1:  # Verifica se é o último elemento
               RouteDetail.mapcode += f"[{lat}, {lon}]\n"               
            else: 
               RouteDetail.mapcode += f"[{lat}, {lon}]," 
            i=i+1  
        if indPol == len(polylinesComunidades) - 1:  # Verifica se é o último elemento     
           RouteDetail.mapcode += f"]\n"
        else:
           RouteDetail.mapcode += f"],\n"  
        indPol = indPol+1
    RouteDetail.mapcode += f"];\n"   
         
    RouteDetail.mapcode += f"let polyComunidades = [];"    
    i=0
    for polyline in polylinesComunidades: 
        RouteDetail.mapcode += f"polyTmp = L.polygon(listComunidades[{i}], {{ color: 'rgb(102,0,204)',fillColor: 'rgb(102,0,204)',fillOpacity: 0.3, weight: 1}}).addTo(map);\n"  
        RouteDetail.mapcode += f"polyComunidades.push(polyTmp);\n"          
        i=i+1  
    return RouteDetail            
################################################################################
def RouteCompAbrangencia(data,user,pontoinicial,cidade,uf,escopo,distanciaPontos,regioes):
    
    UserData.nome=user
    UserData.AlgoritmoOrdenacaoPontos = data["AlgoritmoOrdenacaoPontos"]
    UserData.RaioDaEstacao = data["RaioDaEstacao"]
    UserData.GpsProximoPonto = data["GpsProximoPonto"]
    
    wLog("GetBoundMunicipio e FiltrarAreasUrbanizadasPorMunicipio")
    
    polMunicipio= sf.GetBoundMunicipio(cidade, uf)
    polMunicipioAreasUrbanizadas= sf.FiltrarAreasUrbanizadasPorMunicipio(cidade, uf)
    
    if(escopo=="AreasUrbanizadas"):  # Opções: "Municipio" ou "AreasUrbanizadas" 
        pontosvisita = GeneratePointsWithinCity(polMunicipioAreasUrbanizadas, regioes, distanciaPontos)  
    else:
        pontosvisita = GeneratePointsWithinCity(polMunicipio, regioes, distanciaPontos)
    
    regioes = AtualizaRegioesBoudingBoxPontosVisita(regioes,pontosvisita)
    PreparaServidorRoteamento(regioes)
    RouteDetail = ClRouteDetailList()
    RouteDetail.pontoinicial=pontoinicial
    
    RouteDetail = ServerSetupJavaScript(RouteDetail)   
    RouteDetail.mapcode += f"    const TipoRoute = 'CompAbrangencia';\n"  
    RouteDetail = DesenhaComunidades(RouteDetail,regioes)

    RouteDetail = DesenhaMunicipioAreasUrbanizadas(RouteDetail,cidade,polMunicipioAreasUrbanizadas)
    RouteDetail = DesenhaMunicipio(RouteDetail,cidade,polMunicipio)
        
    wLog("Ordenando e processando Pontos de Visita:")
  
    pontosvisita = OrdenarPontos(pontosvisita,pontoinicial) 
    RouteDetail = PlotaPontosVisita(RouteDetail,pontosvisita,[])
    
    RouteDetail=DesenhaRegioes(RouteDetail,regioes)
    RouteDetail.GeraMapPolylineCaminho()
      
      
          
    fileMap,fileNameStatic,fileKml=GeraArquivosSaida(RouteDetail,'CompAbrangencia')      
    return fileMap,fileNameStatic,fileKml
################################################################################
def GeraArquivosSaida(RouteDetail,tipoServico):
    buf = TimeStringTmp()   
    fileMap = f"WebRotas{tipoServico}{buf}.html"     
    fileName = f"templates/{fileMap}"
    gm.GeraMapaLeaflet(fileName,RouteDetail)
    
    fileMapStatic = f"WebRotas{tipoServico}Static{buf}.html"     
    fileNameStaticF = f"templates/{fileMapStatic}"
    gm.GeraMapaLeaflet(fileNameStaticF,RouteDetail,static=True)
    
    fileKml = f"WebRotas{tipoServico}{buf}.kml"     
    fileKmlF = f"templates/{fileKml}"    
    # GerarKml(pontosvisita,fileKmlF)    
    Gerar_Kml(RouteDetail.coordinates, RouteDetail.pontosvisitaDados,filename=fileKmlF)
    
    return fileMap,fileMapStatic,fileKml
################################################################################
import base64
import mimetypes
################################################################################
def FileToDataUrlBase64(file_path):
    """
    Gera a URL no formato data:@file/<extension>;base64,<data>

    :param file_path: Caminho para o arquivo.
    :return: String no formato data URL.
    """
    try:
        # Detecta o tipo MIME do arquivo
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Se não conseguir detectar o tipo MIME, usa binário como padrão
        if not mime_type:
            mime_type = "application/octet-stream"

        # Lê o conteúdo do arquivo e o codifica em base64
        with open(file_path, "rb") as file:
            encoded_data = base64.b64encode(file.read()).decode("utf-8")

        # Monta a URL no formato data
        data_url = f"data:{mime_type};base64,{encoded_data}"

        return data_url
    except Exception as e:
        raise ValueError(f"Erro ao processar o arquivo: {e}")
################################################################################
# Exemplo de uso
# file_path = "caminho_para_o_arquivo.png"
# data_url = file_to_data_url(file_path)
# print(data_url)

################################################################################
def DeclaracaopontosvisitaDadosJS(pontosvisitaDados):
    """
    Gera uma declaração em JavaScript para uma lista de pontos.

    Args:
        dados (list): Lista de pontos no formato [lat, lon, tipo, descrição].

    Returns:
        str: String contendo a declaração JavaScript.
    """
    # Gerar o array formatado
    i=0
    # [-22.88169706392197, -43.10262976730735,"P0","Local", "Descrição","Altitude","Ativo"],
    js_array = "[\n"
    for ponto in pontosvisitaDados:
        js_array += f"    [{ponto[0]}, {ponto[1]},\"{ponto[2]}\",\"{ponto[3]}\", \"{ponto[4]}\",\"{ponto[5]}\",\"Ativo\"],\n"
        i=i+1
    js_array = js_array.rstrip(",\n") + "\n]"  # Remover a última vírgula e adicionar fechamento

    # Criar a declaração completa
    js_code = "// Formato pontosvisitaDados - [-22.88169706392197, -43.10262976730735,\"P0\",\"Local\", \"Descrição\",\"Altitude\",\"Ativo\"]\n"
    js_code = js_code+ f"var pontosvisitaDados = {js_array};\n"
    return js_code
################################################################################
def PegaLinhaPontosVisitaDados(pontosvisitaDados,lat,lon):
    for linha in pontosvisitaDados: 
        # wLog(f"linha - lat,lon - {lat},{lon} - {linha}")  
        if(linha[0]==lat and linha[1]==lon): 
          
           return linha 
    # wLog("PegaLinhaPontosVisitaDados - falhou")  
    # wLog(f"linha - {linha}") 
    return ""
################################################################################
def GeraPontosVisitaDados(pontosvisita):
    i=0
    pontosvisitaDados=[]
    for ponto in pontosvisita:
        lat, lon = ponto    
        alt=0
        dado = (lat, lon,f"P{i}","Local","",alt)
        pontosvisitaDados.append(dado)   
        i=i+1     
    return pontosvisitaDados
################################################################################
def MesmaOrdenacaoPontosVisita(pontosvisitaDados,pontosvisita,new=False):
    pontosvisitaDadosNew=[]
    i=0
    for ponto in pontosvisita:
        latitude, longitude = ponto
        linha=PegaLinhaPontosVisitaDados(pontosvisitaDados,latitude,longitude)    
        alt=0
        if(new):
           lin2=linha[3] 
           lin3=linha[4] 
        else:
           lin2=linha[2]
           lin3=linha[3]        
        dado = (latitude, longitude,f"P{i}",lin2,lin3,alt)
        pontosvisitaDadosNew.append(dado)
        i=i+1
    return pontosvisitaDadosNew
################################################################################
def get_formatted_timestamp():
    now = datetime.datetime.now()
    return now.strftime("%Y/%m/%d_%H:%M:%S")  
################################################################################
def DeclaraArrayRotas(RouteDetail):
    # var estruturas = []; // Array vazio
    # Salvar
    # sessionStorage.setItem('sessionId', 'abc123');
    # // Recuperar
    # const sessionId = sessionStorage.getItem('sessionId');
    # AAAAAAAAAAAAAAAAAAAAAAAa
    timeStp=get_formatted_timestamp()
    RouteDetail.mapcode += f"    var ListaRotasCalculadas = [];\n"
    RouteDetail.mapcode += f"    var bufdados = {{}};\n"
    RouteDetail.mapcode += f"    bufdados.id = 0;\n"    
    RouteDetail.mapcode += f"    bufdados.time = '{timeStp}';\n"    
    RouteDetail.mapcode += f"    bufdados.polylineRotaDat = [];\n"
    RouteDetail.mapcode += f"    bufdados.pontosvisitaDados = pontosvisitaDados;\n"
    RouteDetail.mapcode += f"    bufdados.pontosVisitaOrdenados = pontosVisitaOrdenados;\n"    
    RouteDetail.mapcode += f"    bufdados.pontoinicial = [{RouteDetail.pontoinicial[0]},{RouteDetail.pontoinicial[1]},'{RouteDetail.pontoinicial[2]}'];\n"
    RouteDetail.mapcode += f"    bufdados.DistanceTotal = {RouteDetail.DistanceTotal/1000};\n"
    RouteDetail.mapcode += f"    bufdados.rotaCalculada = 1;\n" # Rota calculada pelo WebRotas
    RouteDetail.mapcode += f"    ListaRotasCalculadas.push(bufdados);\n"
    
    return RouteDetail   
################################################################################
def PegaAltitudesPVD(pontosvisitaDados):
    # [-22.930538837645273, -43.25880584301294,"P0","Local", "","0","Ativo"],
    for i in range(len(pontosvisitaDados)):
        ponto = pontosvisitaDados[i]
        lat = ponto[0]
        lon = ponto[1]
        alt = AltitudeOpenElevation(lat, lon)
        pontosvisitaDados[i] = (lat, lon, ponto[2], ponto[3], ponto[4], alt)
    return pontosvisitaDados
################################################################################
def PegaAltitudesPVD_Batch(pontosvisitaDados): # Batch faz chamadas em lote para o OpenElevation
    batch_size = 100
    for i in range(0, len(pontosvisitaDados), batch_size):
        batch = pontosvisitaDados[i:i + batch_size]
        altitudes = AltitudeOpenElevationBatch(batch,batch_size)
        for j in range(len(batch)):
            ponto = batch[j]
            lat, lon = ponto[0], ponto[1]
            alt = altitudes[j]
            pontosvisitaDados[i + j] = (lat, lon, ponto[2], ponto[3], ponto[4], alt)

    return pontosvisitaDados
################################################################################
def PlotaPontosVisita(RouteDetail,pontosvisita,pontosvisitaDados):
    wLog("PlotaPontosVisita") 
    i=0 
    RouteDetail.mapcode += f"    var RaioDaEstacao = {UserData.RaioDaEstacao};\n"
    RouteDetail.mapcode += f"    var GpsProximoPonto = '{UserData.GpsProximoPonto}';\n"
    RouteDetail.mapcode += f"    var pontosVisitaOrdenados = [\n"
    
    
    for ponto in pontosvisita:
        latitude, longitude = ponto
        if i == len(pontosvisita) - 1:  # Verifica se é o último elemento
           RouteDetail.mapcode += f"       [{latitude}, {longitude}]"   
        else: 
           RouteDetail.mapcode += f"       [{latitude}, {longitude}]," 
        i=i+1   
        # print(f"  Latitude: {latitude}, Longitude: {longitude}")
    RouteDetail.mapcode += f"    ];\n"

    if(pontosvisitaDados!=[]):
        pontosvisitaDados=MesmaOrdenacaoPontosVisita(pontosvisitaDados,pontosvisita,new=False)
        pontosvisitaDados = PegaAltitudesPVD_Batch(pontosvisitaDados)  # Batch faz chamadas em lote para o OpenElevation
        RouteDetail.mapcode += DeclaracaopontosvisitaDadosJS(pontosvisitaDados)
    else:
        pontosvisitaDados = GeraPontosVisitaDados(pontosvisita) 
        pontosvisitaDados=MesmaOrdenacaoPontosVisita(pontosvisitaDados,pontosvisita,new=True)
        pontosvisitaDados = PegaAltitudesPVD_Batch(pontosvisitaDados) # Batch faz chamadas em lote para o OpenElevation
        RouteDetail.mapcode += DeclaracaopontosvisitaDadosJS(pontosvisitaDados)   
       
      
    RouteDetail.pontosvisitaDados = pontosvisitaDados
    # Criar um mapa  
    # RouteDetail.mapcode += f"    const map = L.map('map');\n"
    RouteDetail.mapcode += f"    map.fitBounds(L.latLngBounds(pontosVisitaOrdenados));\n"        
    # RouteDetail.pontoinicial
    lat = RouteDetail.pontoinicial[0]    
    lon = RouteDetail.pontoinicial[1]  
    desc = RouteDetail.pontoinicial[2] 
     
    RouteDetail.mapcode += f"         mrkPtInicial = L.marker([{lat}, {lon}]).addTo(map).setIcon(createSvgIconColorAltitude('i',10000));\n"      
    RouteDetail.mapcode += f"         mrkPtInicial.bindTooltip('{desc}', {{permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'}});\n"   
    ##############################################
    # Calcula rota entre os pontos os pontos a serem visitados
    (latf,lonf) = pontosvisita[0] 
    RouteDetail=GenerateRouteMap(RouteDetail,lat,lon,latf,lonf)   # Faz a primeira rota saindo do ponto inicial ao primeiro ponto de visita
    i=0
    RouteDetail.mapcode += "var markerVet = [];";
    for ponto in pontosvisita:
        lat, lon = ponto        
 
        # altitude = AltitudeAnatelServer(lat,lon)
        altitude = AltitudePontoVisita(pontosvisitaDados, lat, lon) 
        Descricao=DescricaoPontoVisita(pontosvisitaDados, lat, lon)
             
        RouteDetail.mapcode += f"         markerbufTemp = L.marker([{lat}, {lon}]).addTo(map).on('click', onMarkerClick).setIcon(createSvgIconColorAltitude({i},{altitude}));\n"   
        RouteDetail.mapcode += f"         markerbufTemp._icon.setAttribute('data-id', '{i}'); markerbufTemp._icon.setAttribute('clicado', '0'); markerbufTemp._icon.setAttribute('tamanho', 'full'); markerbufTemp._icon.setAttribute('altitude', '{altitude}');\n"         
        RouteDetail.mapcode += f"         markerbufTemp.bindTooltip('Altitude: {altitude}<br>{Descricao}', {{permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'}});\n"   
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
    ##############################################
    RouteDetail = DeclaraArrayRotas(RouteDetail)    
    RouteDetail.mapcode +="           const defaultIcon = markerVet[1].getIcon();\n"      
    return RouteDetail
################################################################################
def PegaPontosVisita(pontosvisitaDados):
    pontosvisita=[]
    pontosvisita = [[ponto[0], ponto[1]] for ponto in pontosvisitaDados]
    return pontosvisita
################################################################################
def DescricaoPontoVisita(pontosvisitaDados, lat, lon):
    for ponto in pontosvisitaDados:
        if ponto[0] == lat and ponto[1] == lon:
            return ponto[4]  # Retorna o campo de endereço (4º elemento)
    return "Endereço não encontrado para a latitude e longitude fornecidas."
################################################################################
def AltitudePontoVisita(pontosvisitaDados, lat, lon):
    for ponto in pontosvisitaDados:
        if ponto[0] == lat and ponto[1] == lon:
            return ponto[5] # Retorna o campo de altitude (5º elemento)  
    return "Endereço não encontrado para a latitude e longitude fornecidas."
################################################################################
def RoteamentoOSMR(porta,pontosvisita,pontoinicial,recalcularrota):
    UserData.OSMRport=porta
    RouteDetail = ClRouteDetailList()
    # Calcula trecho de roto do pontoinicial ao primeiro ponto de visita
    (latfI,lonfI) = pontosvisita[0]
    wLog(f"RoteamentoOSMR - pontosvisita[0] {latfI},{lonfI}")
    wLog(f"RoteamentoOSMR - pontoinicial {pontoinicial[0]},{pontoinicial[1]}")
    wLog("Pontos de Visita antes ordenação:")
    for ponto in pontosvisita:
        wLog(f"Latitude: {ponto[0]}, Longitude: {ponto[1]}")
    
    if(recalcularrota==1):
        wLog(f"Reordenando pontos de visita")
        pontosvisita=OrdenarPontosDistanciaOSMRMultiThread(pontosvisita,pontoinicial) 
        
    wLog("Pontos de Visita apos ordenação:")
    for ponto in pontosvisita:
        wLog(f"Latitude: {ponto[0]}, Longitude: {ponto[1]}")
        
    RouteDetail=GenerateRouteMap(RouteDetail,pontoinicial[0],pontoinicial[1],latfI,lonfI)
    
    for i in range(len(pontosvisita) - 1):
        lati, loni = pontosvisita[i]
        latf, lonf = pontosvisita[i + 1]
        RouteDetail = GenerateRouteMap(RouteDetail, lati, loni, latf, lonf)
    
    """
    i = 0
    for ponto in pontosvisita:
        # lat, lon = ponto        

        if(i==0):
           (latfI,lonfI) = pontosvisita[i] 
        if(i==(len(pontosvisita) -1)):
           (latfF,lonfF) = pontosvisita[i]            
        if(i>0):
            (lati,loni) = pontosvisita[i-1]
            (latf,lonf) = pontosvisita[i]       
            RouteDetail=GenerateRouteMap(RouteDetail,lati,loni,latf,lonf)
        i=i+1   
    """     
    
    return RouteDetail.coordinates,RouteDetail.DistanceTotal,pontosvisita
################################################################################
def RoutePontosVisita(data,user,pontoinicial,pontosvisitaDados,regioes):
    
    UserData.nome=user
    UserData.AlgoritmoOrdenacaoPontos = data["AlgoritmoOrdenacaoPontos"]
    UserData.RaioDaEstacao = data["RaioDaEstacao"]
    UserData.GpsProximoPonto = data["GpsProximoPonto"]
    
    pontosvisita=PegaPontosVisita(pontosvisitaDados)
    regioes = AtualizaRegioesBoudingBoxPontosVisita(regioes,pontosvisita)
    PreparaServidorRoteamento(regioes)
    RouteDetail = ClRouteDetailList()
    RouteDetail.pontoinicial=pontoinicial
           
    RouteDetail = ServerSetupJavaScript(RouteDetail)     
    RouteDetail.mapcode += f"    const TipoRoute = 'PontosVisita';\n"   
    RouteDetail = DesenhaComunidades(RouteDetail,regioes)
    
    # Criar um mapa centrado no ponto central
    # RouteDetail.mapcode += f"    const map = L.map('map').setView(13);\n"
    
    # Processa Pontos de Visita
    wLog("Ordenando e processando Pontos de Visita:")
    pontosvisita=OrdenarPontos(pontosvisita,pontoinicial) 
    
    RouteDetail = PlotaPontosVisita(RouteDetail,pontosvisita,pontosvisitaDados)
    RouteDetail=DesenhaRegioes(RouteDetail,regioes)
    RouteDetail.GeraMapPolylineCaminho()

    # servidor temp     python3 -m http.server 8080
    #           
    fileMap,fileNameStatic,fileKml=GeraArquivosSaida(RouteDetail,'PontosVisita')
    return fileMap,fileNameStatic,fileKml
###########################################################################################################################
import math
###########################################################################################################################
def AtualizaRegioesBoudingBoxPontosVisita(regioes,pontosvisita,distancia_km=50):
    lat_min,lat_max,lon_min,lon_max = calcula_bounding_box_pontos(pontosvisita, margem_km=50)
    # 1 grau de latitude = 111 km
    # graus_lat = distancia_km / 111.0
    # lat_min = lat_min- graus_lat;
    # lat_max = lat_max+ graus_lat;    
    # lon_min = lon_min- graus_lat;   
    # lon_max = lon_max+ graus_lat;   
    
    NewRegioes = []
    
    regioesglobal = {
            "nome": "regiaoBoundingbox",
            "coord": [
                [lat_max, lon_min],     
                [lat_max, lon_max],        
                [lat_min, lon_max],       
                [lat_min, lon_min],         
            ]
        }   

    NewRegioes.append(regioesglobal)
    for regiao in regioes:
        nome = regiao.get("nome", "SemNome").replace(" ", "_")
        coordenadas = regiao.get("coord", [])
        regiaook = {"nome" : nome, "coord": coordenadas}
        NewRegioes.append(regiaook)
    return NewRegioes
###########################################################################################################################
def calcula_bounding_box_pontos(pontos, margem_km=50):
    """
    Calcula um bounding box expandido em torno de um grupo de pontos.

    Args:
        pontos (list): Lista de coordenadas [(lat, lon), ...].
        margem_km (float): Margem adicional em km ao redor do grupo de pontos.

    Returns:
        dict: Limites do bounding box (lat_min, lat_max, lon_min, lon_max).
    """
    if not pontos:
        raise ValueError("A lista de pontos não pode estar vazia.")
    
    # Determina os limites mínimos e máximos de latitude e longitude
    lat_min = min(p[0] for p in pontos)
    lat_max = max(p[0] for p in pontos)
    lon_min = min(p[1] for p in pontos)
    lon_max = max(p[1] for p in pontos)

    # Latitude média para ajustar a conversão de longitude
    lat_media = (lat_min + lat_max) / 2

    # 1 grau de latitude é aproximadamente 111 km
    desloc_lat = margem_km / 111.0

    # 1 grau de longitude varia com o cosseno da latitude
    desloc_lon = margem_km / (111.0 * math.cos(math.radians(lat_media)))

    # Adiciona a margem
    lat_min -= desloc_lat
    lat_max += desloc_lat
    lon_min -= desloc_lon
    lon_max += desloc_lon

    return lat_min,lat_max,lon_min,lon_max

###########################################################################################################################
def RouteContorno(data,user,pontoinicial,central_point,regioes,radius_km=5, num_points=8):
    # Coordenadas do ponto central (latitude, longitude)
    # central_point = [40.712776, -74.005974]  # Exemplo: Nova York
    #central_point = [-22.90941986104239, -43.16486081793237] # Santos Dumont
    # central_point = [-22.891147608655164, -43.05261174054559] #   Niteroi IFR
    # central_point = [-21.701103198880247, -41.308194753766394] #   Aeroporto de Campos
 
    #central_point = [-22.9864182585604, -43.37041245345915] 
    
    UserData.nome=user
    UserData.AlgoritmoOrdenacaoPontos = data["AlgoritmoOrdenacaoPontos"]
    UserData.RaioDaEstacao = data["RaioDaEstacao"]
    UserData.GpsProximoPonto = data["GpsProximoPonto"]
   
    # Coordenadas da rota (exemplo de uma rota circular simples)   

    pontosvisita = GeneratePointsAround(latitude=central_point[0], longitude=central_point[1], radius_km=radius_km, num_points=num_points)
    
    regioes = AtualizaRegioesBoudingBoxPontosVisita(regioes,pontosvisita)
    
    PreparaServidorRoteamento(regioes)
    
    RouteDetail = ClRouteDetailList()
    RouteDetail.pontoinicial=pontoinicial
    
    RouteDetail = ServerSetupJavaScript(RouteDetail)  
    RouteDetail.mapcode += f"    const TipoRoute = 'DriveTest';\n"
    RouteDetail = DesenhaComunidades(RouteDetail,regioes)
    
    # Criar um mapa centrado no ponto central
    # RouteDetail.mapcode += f"    const map = L.map('map').setView([{central_point[0]}, {central_point[1]}], 13);\n"
    RouteDetail.mapcode += f"     map.setView([{central_point[0]}, {central_point[1]}], 13);\n"
    
    # Adicionar uma marca no ponto central
    RouteDetail.mapcode += f"    var markerCentral = L.marker([{central_point[0]}, {central_point[1]}]).addTo(map); \n"
    RouteDetail.mapcode += f"    markerCentral.bindTooltip('Ponto Central', {{permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'}});\n"   
    RouteDetail.mapcode += "     markerCentral.setIcon(iMarquerVerde);\n"

    pontosvisita = OrdenarPontos(pontosvisita,pontoinicial) 
    RouteDetail = PlotaPontosVisita(RouteDetail,pontosvisita,[])
 
    RouteDetail=DesenhaRegioes(RouteDetail,regioes)
    RouteDetail.GeraMapPolylineCaminho()
    # GerarKml(coordenadasrota, filename="rota.kml")
    
    # servidor temp     python3 -m http.server 8080
    #           
    fileMap,fileNameStatic,fileKml=GeraArquivosSaida(RouteDetail,'Contorno')
    return fileMap,fileNameStatic,fileKml
###########################################################################################################################
def main():
    return
###########################################################################################################################
if __name__ == "__main__":
    main()
###########################################################################################################################    
