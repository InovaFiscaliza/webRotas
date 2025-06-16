###########################################################################################################################
import os
import psutil
import math
import threading
from concurrent.futures import ThreadPoolExecutor
import datetime
from itertools import permutations
import time
import requests
import math
import numpy as np
import polyline
from shapely.geometry import Point, Polygon, box
import shapely.ops
from geopy.distance import geodesic
import base64
import mimetypes
import pyproj

import shapeFiles as sf
import geraMapa as gm
import routing_servers_interface as si
import CacheBoundingBox as cb
import regions as rg
import GuiOutput as gi
from ClRouteDetail import ClRouteDetailList
from wlog import wLog


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
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distância em metros
    distancia = R * c

    return distancia


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
    params = {"locations": f"{latitude},{longitude}"}

    def fetch_elevation(url):
        try:
            # Faz a requisição à API
            response = requests.get(
                url, params=params, timeout=10
            )  # Timeout de 10 segundos

            # Verifica se a requisição foi bem-sucedida
            response.raise_for_status()

            # Tenta decodificar o JSON da resposta
            data = response.json()

            # Verifica se a resposta contém os dados esperados
            if "results" in data and len(data["results"]) > 0:
                return round(data["results"][0]["elevation"])
            else:
                wLog(
                    "getElevationOpenElev Erro: Resposta da API não contém dados válidos.",
                    level="debug",
                )
                return 0

        except requests.exceptions.RequestException as e:
            # Captura erros relacionados à requisição (conexão, timeout, etc.)
            wLog(f"getElevationOpenElev Erro na requisição: {e}")
            raise  # Re-lança a exceção para ser capturada no bloco externo

        except ValueError as e:
            # Captura erros de decodificação JSON
            wLog(f"getElevationOpenElev Erro ao decodificar JSON: {e}")
            return 0

        except KeyError as e:
            # Captura erros de chave ausente no JSON
            wLog(f"getElevationOpenElev Erro no formato da resposta: {e}")
            return 0

    try:
        return fetch_elevation(url)
    except requests.exceptions.RequestException:
        # Se a requisição à URL principal falhar, tenta a URL alternativa
        wLog("Tentando URL alternativa (VPN)...")
        return fetch_elevation(urlVpn)


###########################################################################################################################
def getElevationOpenElevBatch(lat_lons, batch_size):
    """
    Obtém a elevação de múltiplas localizações usando a API Open-Elevation em lotes.

    Args:
        lat_lons (list): Lista de tuplas contendo latitude e longitude.
        batch_size (int): Tamanho do lote para processamento.

    Returns:
        list: Lista de elevações em metros. Retorna 0 para coordenadas com erro.
    """
    url = "https://api.open-elevation.com/api/v1/lookup"
    urlVpn = "http://rhfisnspdex02.anatel.gov.br/api/v1/lookup"
    elevations = []

    def fetch_batch_elevations(url, batch):
        """Função interna para buscar elevações de um lote."""
        locations = "|".join([f"{lat},{lon}" for lat, lon in batch])
        params = {"locations": locations}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "results" in data:
                return [round(res["elevation"]) for res in data["results"]]
            else:
                return [0] * len(batch)
        except (requests.exceptions.RequestException, ValueError, KeyError):
            return [0] * len(batch)

    for i in range(0, len(lat_lons), batch_size):
        batch = lat_lons[i : i + batch_size]
        batch_elevations = fetch_batch_elevations(url, batch)

        if all(
            e == 0 for e in batch_elevations
        ):  # Se todos os valores forem 0, tenta a VPN
            batch_elevations = fetch_batch_elevations(urlVpn, batch)

        elevations.extend(batch_elevations)

    return elevations


###########################################################################################################################
MinAltitude = 50000  # Valor alto para garantir que a primeira altitude seja menor
MaxAltitude = 0


###########################################################################################################################
def ResetAltitudes():
    global MinAltitude
    global MaxAltitude
    MinAltitude = 50000
    MaxAltitude = 0
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
def AltitudeOpenElevationBatch(batch, batch_size):
    global MinAltitude
    global MaxAltitude
    ResetAltitudes()
    lat_lons = [(p[0], p[1]) for p in batch]
    altitudes = getElevationOpenElevBatch(lat_lons, batch_size)
    if altitudes:  # Verifica se a lista não está vazia
        MinAltitude = min(MinAltitude, min(altitudes))
        MaxAltitude = max(MaxAltitude, max(altitudes))
        MinAltitude = int(MinAltitude)
        MaxAltitude = int(MaxAltitude)
    return altitudes


###########################################################################################################################
def Gerar_Kml(polyline_rota, pontos_visita_dados, filename="rota.kml"):
    # Cabeçalho do KML
    kml_inicio = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>WebRotas Pontos e Rotas</name>
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
    kml_polyline = ""
    for ind, polyLineTmp in enumerate(polyline_rota):
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

    wLog(f"Arquivo KML '{filename}' gerado com sucesso!", level="debug")


###########################################################################################################################
ServerTec = "OSMR"


###########################################################################################################################
def GetRouteFromServer(start_lat, start_lon, end_lat, end_lon):

    # Tenta buscar do cache
    cached_response = cb.cCacheBoundingBox.route_cache_get(
        start_lat, start_lon, end_lat, end_lon
    )
    if cached_response is not None:
        wLog(
            f"Usando rota do cache para: {start_lat},{start_lon},{end_lat},{end_lon}",
            level="debug",
        )
        return cached_response

    # Coordenadas de início e fim
    start_coords = (start_lat, start_lon)
    end_coords = (end_lat, end_lon)

    if ServerTec == "OSMR":
        # URL da solicitação ao servidor OSMR
        url = f"http://localhost:{UserData.OSMRport}/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline&steps=true"

    wLog(url, level="debug")
    # Fazer a solicitação
    response = requests.get(url)
    # fazer o cache da solicitação
    cb.cCacheBoundingBox.route_cache_set(
        start_lat, start_lon, end_lat, end_lon, response
    )
    return response


###########################################################################################################################
def GenerateRouteMap(RouteDetailLoc, start_lat, start_lon, end_lat, end_lon):
    if ServerTec == "OSMR":
        return GenerateRouteMapOSMR(
            RouteDetailLoc, start_lat, start_lon, end_lat, end_lon
        )
    return RouteDetailLoc


###########################################################################################################################
def GenerateRouteMapOSMR(RouteDetailLoc, start_lat, start_lon, end_lat, end_lon):
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
    if response.status_code == 200 and "routes" in data:
        route = data["routes"][0]
        geometry = route["geometry"]
        coordinates = polyline.decode(geometry)
        RouteDetailLoc.coordinates.append(coordinates)
        RouteDetailLoc.DistanceTotal = (
            RouteDetailLoc.DistanceTotal + calcular_distancia_totalOSMR(data)
        )
    else:
        wLog(f"Erro na solicitação: {data}", level="debug")
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
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(radius_km / R)
            + math.cos(lat_rad) * math.sin(radius_km / R) * math.cos(angle)
        )

        # Calcular a nova longitude
        new_lon_rad = lon_rad + math.atan2(
            math.sin(angle) * math.sin(radius_km / R) * math.cos(lat_rad),
            math.cos(radius_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad),
        )

        # Converter de radianos para graus
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)

        points.append((new_lat, new_lon))

    return points


###########################################################################################################################
def TimeStringTmp():
    # Obtém a data e hora atuais
    agora = datetime.datetime.now()
    # Formata a data e hora em uma string no formato AAAA-MM-DD_HH-MM-SS
    buf = agora.strftime("%Y-%m-%d_%H-%M-%S")
    return buf


###########################################################################################################################
def medir_tempo_execucao(funcao, *args, **kwargs):
    inicio = time.perf_counter()  # alta resolução
    resultado = funcao(*args, **kwargs)
    fim = time.perf_counter()
    tempo_execucao = fim - inicio
    return tempo_execucao


###########################################################################################################################
def estimar_tempo_ordenacao(pontosvisita):
    if UserData.AlgoritmoOrdenacaoPontos == "DistanciaOSMRMultiThread":
        tempo_uma_rota = medir_tempo_execucao(
            DistanciaRota,
            pontosvisita[0][0],
            pontosvisita[0][1],
            pontosvisita[1][0],
            pontosvisita[1][1],
        )
        cpu_count = psutil.cpu_count(
            logical=True
        )  # threads lógicas, incluindo hyper-threading
        if not pontosvisita:
            return 0  # Nenhum ponto, nenhum tempo
        num_pontos = len(pontosvisita)
        tempo_estimado = (0.5 * num_pontos * num_pontos * tempo_uma_rota) / cpu_count

        # wLog(
        #     f"Depuração: tempo_uma_rota={tempo_uma_rota:.6f}s | cpu_count={cpu_count} | "
        #     f"num_pontos={num_pontos} | tempo_estimado={tempo_estimado:.6f}s",
        #     level="debug"
        # )

        return tempo_estimado
    if UserData.AlgoritmoOrdenacaoPontos == "DistanciaOSMR":
        tempo_uma_rota = medir_tempo_execucao(
            DistanciaRota,
            pontosvisita[0][0],
            pontosvisita[0][1],
            pontosvisita[1][0],
            pontosvisita[1][1],
        )
        if not pontosvisita:
            return 0  # Nenhum ponto, nenhum tempo
        num_pontos = len(pontosvisita)
        tempo_estimado = 0.5 * num_pontos * num_pontos * tempo_uma_rota
        return tempo_estimado
    if UserData.AlgoritmoOrdenacaoPontos == "DistanciaGeodesica":
        tempo_uma_rota = medir_tempo_execucao(
            Haversine,
            pontosvisita[0][0],
            pontosvisita[0][1],
            pontosvisita[1][0],
            pontosvisita[1][1],
        )
        if not pontosvisita:
            return 0  # Nenhum ponto, nenhum tempo
        num_pontos = len(pontosvisita)
        tempo_estimado = 0.5 * num_pontos * num_pontos * tempo_uma_rota
        return tempo_estimado
    if UserData.AlgoritmoOrdenacaoPontos == "TravelingSalesman":
        tempo_uma_rota = medir_tempo_execucao(
            DistanciaRota,
            pontosvisita[0][0],
            pontosvisita[0][1],
            pontosvisita[1][0],
            pontosvisita[1][1],
        )
        if not pontosvisita:
            return 0  # Nenhum ponto, nenhum tempo
        num_pontos = len(pontosvisita)
        tempo_estimado = num_pontos * tempo_uma_rota * math.factorial(num_pontos)
        return tempo_estimado
    return 0


###########################################################################################################################
# Função para ordenar os pontos de visita, pelo ultimo mais próximo, segundo a chatgpt, algoritmo ganancioso...
def OrdenarPontos(pontosvisita, pontoinicial):
    # BenchmarkRotas(pontosvisita,pontoinicial)
    tempoestimado = estimar_tempo_ordenacao(pontosvisita)
    tempoestimado = formatar_tempo_vasto(tempoestimado)
    wLog(
        f"OrdenarPontos - Algoritmo rota otima: [{UserData.AlgoritmoOrdenacaoPontos}] - Tempo estimado: {tempoestimado}"
    )

    if (
        UserData.AlgoritmoOrdenacaoPontos == "DistanciaGeodesica"
    ):  # "DistanciaOSMR", "DistanciaGeodesica", "DistanciaOSMRMultiThread"
        return OrdenarPontosDistanciaGeodesica(pontosvisita, pontoinicial)
    if UserData.AlgoritmoOrdenacaoPontos == "DistanciaOSMR":
        return OrdenarPontosDistanciaOSMR(pontosvisita, pontoinicial)
    if UserData.AlgoritmoOrdenacaoPontos == "DistanciaOSMRMultiThread":
        return OrdenarPontosDistanciaOSMRMultiThread(pontosvisita, pontoinicial)
    if UserData.AlgoritmoOrdenacaoPontos == "TravelingSalesman":
        return OrdenarPontosTSP(pontosvisita, pontoinicial)
    return pontosvisita  # Nenhuma seleção, não ordena os pontos


################################################################################
def formatar_tempo_vasto(segundos):
    # Exemplos de uso
    # print(formatar_tempo(45))             # 45 segundos
    # print(formatar_tempo(120))            # 2 minutos
    # print(formatar_tempo(4000))           # 1.11 horas
    # print(formatar_tempo(90000))          # 1.04 dias
    # print(formatar_tempo(10**8))          # 38.58 anos
    # print(formatar_tempo(10**13))         # 26.43 milhões de anos
    # print(formatar_tempo(10**17))         # 8.77 bilhões de anos
    from decimal import Decimal, getcontext

    getcontext().prec = 1000

    unidades = [
        ("minuto", 60),
        ("hora", 60),
        ("dia", 24),
        ("mês", 30),
        ("ano", 12),
        ("milênio", 1000),
        ("milhão de anos", 1000),
        ("bilhão de anos", 1000),
        ("trilhão de anos", 1000),
        ("quadrilhão de anos", 1000),
        ("quintilhão de anos", 1000),
        ("sextilhão de anos", 1000),
        ("septilhão de anos", 1000),
        ("octilhão de anos", 1000),
        ("nonilhão de anos", 1000),
        ("decilhão de anos", 1000),
        ("undecilhão de anos", 1000),
        ("duodecilhão de anos", 1000),
        ("tredecilhão de anos", 1000),
        ("quattuordecilhão de anos", 1000),
        ("quindecilhão de anos", 1000),
        ("sexdecilhão de anos", 1000),
        ("septendecilhão de anos", 1000),
        ("octodecilhão de anos", 1000),
        ("novemdecilhão de anos", 1000),
        ("vigesilhão de anos", 1000),
        ("centilhão de anos", 1000),
        ("ducentilhão de anos", 1000),
        ("trecentilhão de anos", 1000),
        ("quadringentilhão de anos", 1000),
        ("quingentilhão de anos", 1000),
        ("sescentilhão de anos", 1000),
        ("septingentilhão de anos", 1000),
        ("octingentilhão de anos", 1000),
        ("nongentilhão de anos", 1000),
        ("milhêsilhão de anos", 1000),
        (
            "googol de anos",
            Decimal("1e100"),
        ),  # apena decorativo o valor verdadeiro faz o python falhar  ("googol de anos", 10**100)
        (
            "googolplex de anos",
            Decimal("1e10000"),
        ),  # apena decorativo o valor verdadeiro faz o python falhar ("googolplex de anos", 10**(10**100)),
    ]
    valor = segundos
    nome = "segundo"
    for nome_unidade, fator in unidades:
        if valor < fator:
            break
        valor /= fator
        nome = nome_unidade

    valor_formatado = f"{valor:.2f}".rstrip("0").rstrip(".")
    return f"{valor_formatado} {nome}" + (
        "s" if float(valor_formatado) != 1 and not nome.endswith("s") else ""
    )


################################################################################
# Função paralela para calcular a menor distância
def calcular_menor_distanciaThread(pontosvisita, ultimo_ponto):
    with ThreadPoolExecutor() as executor:
        distancias = executor.map(
            lambda p: (p, DistanciaRota(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1])),
            pontosvisita,
        )
        return min(distancias, key=lambda x: x[1])[
            0
        ]  # Retorna o ponto com menor distância


################################################################################
def OrdenarPontosDistanciaOSMRMultiThread(pontosvisita, pontoinicial):
    ordenados = [
        (pontoinicial[0], pontoinicial[1])
    ]  # Iniciar a lista com o ponto inicial
    pontosvisita_lock = threading.Lock()

    while pontosvisita:
        ultimo_ponto = ordenados[-1]

        # Calcular o próximo ponto mais próximo em paralelo
        with pontosvisita_lock:  # Protege a lista durante a iteração
            proximo_ponto = calcular_menor_distanciaThread(pontosvisita, ultimo_ponto)
            ordenados.append(proximo_ponto)
            pontosvisita.remove(proximo_ponto)

    del ordenados[
        0
    ]  # Remove o primeiro elemento, usado apenas como referência inicial da ordenação
    return ordenados


################################################################################
# Versão baseada no TSP (Traveling Salesman Problem)
def OrdenarPontosTSP(pontosvisita, pontoinicial):
    if not pontosvisita:
        return []

    # Adiciona ponto inicial ao início de cada permutação e calcula o caminho total
    melhor_caminho = None
    menor_distancia = float("inf")

    for perm in permutations(pontosvisita):
        caminho = [pontoinicial] + list(perm)
        distancia_total = 0

        for i in range(len(caminho) - 1):
            distancia_total += DistanciaRota(
                caminho[i][0], caminho[i][1], caminho[i + 1][0], caminho[i + 1][1]
            )

        if distancia_total < menor_distancia:
            menor_distancia = distancia_total
            melhor_caminho = perm

    return list(melhor_caminho)


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
    if response.status_code == 200 and "routes" in data:
        return calcular_distancia_totalOSMR(data)
    else:
        wLog("DistanciaRota - erro pegando rota OSMR")
        quit()
    return 0


################################################################################
def DistanciaRotaTotal(pontosvisita):
    i = 0
    dist = 0
    for i in range(len(pontosvisita) - 1):
        dist += DistanciaRota(
            pontosvisita[i][0],
            pontosvisita[i][1],
            pontosvisita[i + 1][0],
            pontosvisita[i + 1][1],
        )
        i = i + 1
    return dist


################################################################################
# Função para ordenar os pontos de visita, metrica OSMR, pelo ultimo mais próximo, algoritmo ganancioso.
def OrdenarPontosDistanciaOSMR(pontosvisita, pontoinicial):
    ordenados = [
        (pontoinicial[0], pontoinicial[1])
    ]  # Iniciar a lista com o ponto inicial
    while pontosvisita:
        ultimo_ponto = ordenados[
            -1
        ]  # Obtém o último ponto adicionado à lista 'ordenados'
        proximo_ponto = min(
            pontosvisita,
            key=lambda p: DistanciaRota(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1]),
        )
        ordenados.append(proximo_ponto)
        pontosvisita.remove(proximo_ponto)
    del ordenados[
        0
    ]  # Remove o primeiro elemento, usado apenas como referência de inicial da ordenação
    return ordenados


################################################################################
# Função para ordenar os pontos de visita, metrica Distâcia Geodesica , pelo ultimo mais próximo, algoritmo ganancioso.
def OrdenarPontosDistanciaGeodesica(pontosvisita, pontoinicial):
    ordenados = [
        (pontoinicial[0], pontoinicial[1])
    ]  # Iniciar a lista com o ponto inicial
    while pontosvisita:
        ultimo_ponto = ordenados[-1]
        proximo_ponto = min(
            pontosvisita,
            key=lambda p: Haversine(ultimo_ponto[0], ultimo_ponto[1], p[0], p[1]),
        )
        ordenados.append(proximo_ponto)
        pontosvisita.remove(proximo_ponto)
    del ordenados[
        0
    ]  # Remove o primeiro elemento, usado apenas como referência de inicial da ordenação
    return ordenados


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
        wLog(f"Erro ao executar a função: {e}")
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
def BenchmarkRotas(pontosvisita, pontoinicial):
    # 2024-12-28 23:11:33 : ---------------------------------------------------------------------------------------------
    # 2024-12-28 23:11:33 : BenchmarkRotas
    # 2024-12-28 23:34:42 : Tempo ordenacao geodesica: 00:00:001 minutos - Distancia rota: 250 km
    # 2024-12-28 23:34:42 : Tempo ordenacao OSMR: 17:56:159 minutos - Distancia rota: 158 km
    # 2024-12-28 23:34:42 : Tempo ordenacao OSMR MultiThread: 02:03:077 minutos - Distancia rota: 158 km
    # 2024-12-28 23:34:42 : ---------------------------------------------------------------------------------------------

    wLog(
        "---------------------------------------------------------------------------------------------"
    )
    wLog("BenchmarkRotas")
    # ---------------------------------------
    pontosvisitaBench = pontosvisita.copy()
    pontosvisitaBench, tempoGeo = CronometraFuncao(
        OrdenarPontosDistanciaGeodesica, pontosvisitaBench, pontoinicial
    )
    tempoGeo = formatar_tempo(tempoGeo)
    distGeo = int(DistanciaRotaTotal(pontosvisitaBench) / 1000)
    # ---------------------------------------
    pontosvisitaBench = pontosvisita.copy()
    pontosvisitaBench, tempoOsmr = CronometraFuncao(
        OrdenarPontosDistanciaOSMR, pontosvisitaBench, pontoinicial
    )
    tempoOsmr = formatar_tempo(tempoOsmr)
    distOsmr = int(DistanciaRotaTotal(pontosvisitaBench) / 1000)
    # ---------------------------------------
    pontosvisitaBench = pontosvisita.copy()
    pontosvisitaBench, tempoOsmrThr = CronometraFuncao(
        OrdenarPontosDistanciaOSMRMultiThread, pontosvisitaBench, pontoinicial
    )
    tempoOsmrThr = formatar_tempo(tempoOsmrThr)
    distOsmrThr = int(DistanciaRotaTotal(pontosvisitaBench) / 1000)
    # ---------------------------------------
    wLog(
        f"Tempo ordenação geodesica: {tempoGeo} minutos - Distancia rota: {distGeo} km"
    )
    wLog(f"Tempo ordenação OSMR: {tempoOsmr} minutos - Distancia rota: {distOsmr} km")
    wLog(
        f"Tempo ordenação OSMR MultiThread: {tempoOsmrThr} minutos - Distancia rota: {distOsmrThr} km"
    )
    wLog(
        "---------------------------------------------------------------------------------------------"
    )
    return


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
        with open(arquivo_saida, "w") as f:
            f.write(f"routingAreas\n")
            for regiao in regioes:
                nome = regiao.get("name", "none").replace(" ", "_")
                coordenadas = regiao.get("coord", [])

                # Escrever o nome da região no arquivo
                f.write(f"{nome}\n")
                wLog(f"Região adicionada: {nome}", level="debug")

                # Escrever as coordenadas da região
                for i, (latitude, longitude) in enumerate(coordenadas):
                    f.write(f"   {longitude} {latitude}\n")

                # Encerrar a definição da região
                f.write("END\n")
            f.write("END\n")
        wLog(f"Arquivo '{arquivo_saida}' gerado com sucesso.", level="debug")

    except Exception as e:
        wLog(f"Erro ao gerar o arquivo .poly: {e}", level="debug")


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


def VerificarServidorAtivo(url, reposta, tentativas=10, intervalo=1):
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


################################################################################
def DesenhaRegioes(RouteDetail, regioes):
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

        RouteDetail.mapcode += f"    regiao{nome} = [\n"
        coordenadas = regiao.get("coord", [])
        wLog(f"  Região: {nome}", level="debug")
        i = 0
        for coord in coordenadas:
            latitude, longitude = coord
            if i == len(coordenadas) - 1:  # Verifica se é o último elemento
                RouteDetail.mapcode += f"       [{latitude}, {longitude}]\n"
            else:
                RouteDetail.mapcode += f"       [{latitude}, {longitude}],"
            i = i + 1
        RouteDetail.mapcode += f"    ];\n"
        if RegiaoExclusão:
            RouteDetail.mapcode += f"var polygon{nome} = L.polygon(regiao{nome}, {{ color: 'red',fillColor: 'lightred',fillOpacity: 0.2, weight: 1}}).addTo(map);\n"
        else:
            RouteDetail.mapcode += f"var polygon{nome} = L.polygon(regiao{nome}, {{ color: 'green',fillColor: 'lightgreen',fillOpacity: 0.0, weight: 1}}).addTo(map);\n"
    return RouteDetail


################################################################################
def DesenhaMunicipio(RouteDetail, nome, polMunicipio):
    indPol = 0
    nome = SubstAcentos(nome).replace(" ", "_")
    for poligons in polMunicipio:
        i = 0
        RouteDetail.mapcode += f"    municipio{nome}Pol{indPol} = [\n"
        for coordenada in poligons:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            longitude, latitude = coordenada
            if i == len(poligons) - 1:  # Verifica se é o último elemento
                RouteDetail.mapcode += f"       [{latitude}, {longitude}]]\n"
            else:
                RouteDetail.mapcode += f"       [{latitude}, {longitude}],"
            i = i + 1
        RouteDetail.mapcode += f"var polygonMun{nome}{indPol} = L.polygon(municipio{nome}Pol{indPol}, {{ color: 'green',fillColor: 'lightgreen',fillOpacity: 0.0, weight: 1}}).addTo(map);\n"
        indPol = indPol + 1
    return RouteDetail


################################################################################
def DesenhaMunicipioAreasUrbanizadas(RouteDetail, nome, polMunicipioAreas):
    indPol = 0
    nome = SubstAcentos(nome).replace(" ", "_")
    for poligons in polMunicipioAreas:
        i = 0
        RouteDetail.mapcode += f"    municipioAreasUrbanizadas{nome}Pol{indPol} = [\n"
        for coordenada in poligons:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            longitude, latitude = coordenada
            if i == len(poligons) - 1:  # Verifica se é o último elemento
                RouteDetail.mapcode += f"       [{latitude}, {longitude}]]\n"
            else:
                RouteDetail.mapcode += f"       [{latitude}, {longitude}],"
            i = i + 1
        RouteDetail.mapcode += f"var polygonMunAreasUrbanizadas{nome}{indPol} = L.polygon(municipioAreasUrbanizadas{nome}Pol{indPol}, {{ color: 'rgb(74, 73, 73)',fillColor: 'lightblue',fillOpacity: 0.0, weight: 1, dashArray: '4, 4'}}).addTo(map);\n"
        indPol = indPol + 1
    return RouteDetail


################################################################################
def GeneratePointsWithinCity(city_boundary: list, regioes: list, distance: int) -> list:
    """
    Gera uma lista de pontos (lat, lon) distribuídos dentro da área delimitada por um polígono.

    :param city_boundary: Lista de coordenadas [(lat1, lon1), (lat2, lon2), ...] definindo o polígono da cidade.
    :param distance: Distância em metros entre os pontos.
    :return: Lista de pontos [(lat, lon)] dentro das fronteiras.
    """
    # Converter a lista de coordenadas em um polígono
    polygonsList = []
    for poligonsMun in city_boundary:
        polygonsList.append(
            Polygon([(float(lon), float(lat)) for lat, lon in poligonsMun])
        )  # Shapely usa (x, y)

    polAvoidList = []
    for regiao in regioes:
        nome = regiao.get("nome", "Sem Nome")
        if "!" in nome:
            coordenadas = regiao.get("coord", [])
            polAvoidList.append(
                Polygon([(float(lat), float(lon)) for lat, lon in coordenadas])
            )

    # wLog("Coordenadas externas polygonsList[0]:")
    # for coord in polygonsList[0].exterior.coords:
    #    wLog(coord)

    # wLog("Coordenadas externas polAvoidList[0]:")
    # for coord in polAvoidList[0].exterior.coords:
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
        ref_point = (
            base_point[0] + 0.1,
            base_point[1],
        )  # Um ponto próximo para calcular a relação
        degree_distance = geodesic(base_point, ref_point).meters / 0.1
        return float(distance_m) / float(degree_distance)

    # Calcular passos em latitude e longitude
    lat_step = meter_to_degree((min_lat, min_lon), distance)
    lon_step = meter_to_degree((min_lat, min_lon), distance)

    # Gerar uma grade de pontos
    lat_range = np.arange(min_lat, max_lat, lat_step)
    lon_range = np.arange(min_lon, max_lon, lon_step)

    # Filtrar pontos dentro do polígono
    # points_within_city = []
    # Usar um conjunto para evitar pontos duplicados
    points_within_city = set()

    for lat in lat_range:
        for lon in lon_range:
            point = Point(lon, lat)
            for polygon in polygonsList:
                if polygon.contains(point):
                    insideAvoidRegion = 0
                    for polygonAvoid in polAvoidList:
                        if polygonAvoid.contains(point):
                            insideAvoidRegion = 1
                    if insideAvoidRegion == 0:
                        # points_within_city.append((lon, lat))
                        points_within_city.add((lon, lat))  # Adiciona ao conjunto

    # return points_within_city
    return list(points_within_city)  # Converte o conjunto de volta para uma lista


################################################################################
def ServerSetupJavaScript(RouteDetail):
    if ServerTec == "OSMR":
        RouteDetail.mapcode += f"    const ServerTec = 'OSMR';\n"
        RouteDetail.mapcode += f"    const UserName = '{UserData.nome}';\n"
        RouteDetail.mapcode += f"    const OSRMPort = {UserData.OSMRport};\n"
    return RouteDetail


################################################################################
def calc_km2_regiao(regioes: list, nome_alvo: str = "boundingBoxRegion") -> float:
    """
    Calcula a área em km² da região nomeada dentro da lista de regiões.

    :param regioes: Lista de dicionários contendo as regiões.
    :param nome_alvo: Nome da região alvo para extração do bounding box.
    :return: Área da região em quilômetros quadrados (km²), ou None se a região não for encontrada.
    """
    bbox = rg.extrair_bounding_box_de_regioes(regioes, nome_alvo)
    if not bbox:
        return None

    lon_min, lat_min, lon_max, lat_max = bbox

    # Cria polígono geográfico
    bbox_polygon = box(lon_min, lat_min, lon_max, lat_max)

    # Define projetor para área em metros usando uma projeção equivalente (ex: Albers Equal Area)
    proj = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:6933", always_xy=True
    )  # WGS84 → Equal Area (m)

    # Projeta as coordenadas do bounding box
    projected_polygon = shapely.ops.transform(proj.transform, bbox_polygon)

    # Calcula a área em metros quadrados e converte para km²
    area_km2 = projected_polygon.area / 1_000_000.0

    return round(area_km2, 2)


################################################################################
def get_polyline_comunities(regioes):
    bounding_box = rg.extrair_bounding_box_de_regioes(regioes)
    polylinesComunidades = cb.cCacheBoundingBox.comunidades_cache.get_polylines(regioes)
    if not polylinesComunidades:
        polylinesComunidades = sf.FiltrarComunidadesBoundingBox(bounding_box)
        cb.cCacheBoundingBox.comunidades_cache.add_polyline(
            regioes, polylinesComunidades
        )
    gi.cGuiOutput.json_comunities_create(polylinesComunidades)
    return polylinesComunidades


################################################################################
# polylinesComunidades = get_polyline_comunities(regioes)
def DesenhaComunidades(RouteDetail, polylinesComunidades):

    RouteDetail.mapcode += f"listComunidades = [\n"
    indPol = 0
    for polyline in polylinesComunidades:
        i = 0
        RouteDetail.mapcode += f"[\n"
        for coordenada in polyline:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            lat, lon = coordenada
            if i == len(polyline) - 1:  # Verifica se é o último elemento
                RouteDetail.mapcode += f"[{lat}, {lon}]\n"
            else:
                RouteDetail.mapcode += f"[{lat}, {lon}],"
            i = i + 1
        if indPol == len(polylinesComunidades) - 1:  # Verifica se é o último elemento
            RouteDetail.mapcode += f"]\n"
        else:
            RouteDetail.mapcode += f"],\n"
        indPol = indPol + 1
    RouteDetail.mapcode += f"];\n"

    RouteDetail.mapcode += f"let polyComunidades = [];"
    i = 0
    for polyline in polylinesComunidades:
        RouteDetail.mapcode += f"polyTmp = L.polygon(listComunidades[{i}], {{ color: 'rgb(102,0,204)',fillColor: 'rgb(102,0,204)',fillOpacity: 0.3, weight: 1}}).addTo(map);\n"
        RouteDetail.mapcode += f"polyComunidades.push(polyTmp);\n"
        i = i + 1
    return RouteDetail


################################################################################


def DesenhaComunidadesOLD(RouteDetail, regioes):
    bounding_box = rg.extrair_bounding_box_de_regioes(regioes)

    polylinesComunidades = cb.cCacheBoundingBox.comunidades_cache.get_polylines(regioes)
    if not polylinesComunidades:
        polylinesComunidades = sf.FiltrarComunidadesBoundingBox(bounding_box)
        cb.cCacheBoundingBox.comunidades_cache.add_polyline(
            regioes, polylinesComunidades
        )

    gi.cGuiOutput.json_comunities_create(polylinesComunidades)

    RouteDetail.mapcode += f"listComunidades = [\n"
    indPol = 0
    for polyline in polylinesComunidades:
        i = 0
        RouteDetail.mapcode += f"[\n"
        for coordenada in polyline:
            # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
            lat, lon = coordenada
            if i == len(polyline) - 1:  # Verifica se é o último elemento
                RouteDetail.mapcode += f"[{lat}, {lon}]\n"
            else:
                RouteDetail.mapcode += f"[{lat}, {lon}],"
            i = i + 1
        if indPol == len(polylinesComunidades) - 1:  # Verifica se é o último elemento
            RouteDetail.mapcode += f"]\n"
        else:
            RouteDetail.mapcode += f"],\n"
        indPol = indPol + 1
    RouteDetail.mapcode += f"];\n"

    RouteDetail.mapcode += f"let polyComunidades = [];"
    i = 0
    for polyline in polylinesComunidades:
        RouteDetail.mapcode += f"polyTmp = L.polygon(listComunidades[{i}], {{ color: 'rgb(102,0,204)',fillColor: 'rgb(102,0,204)',fillOpacity: 0.3, weight: 1}}).addTo(map);\n"
        RouteDetail.mapcode += f"polyComunidades.push(polyTmp);\n"
        i = i + 1
    return RouteDetail


################################################################################
def get_areas_urbanas_cache(cidade, uf):
    chave_regiao = {"cidade": cidade, "uf": uf}  # dicionário, compatível com _hash_bbox
    cache_polylines = cb.cCacheBoundingBox.areas_urbanas.get_polylines(chave_regiao)
    if not cache_polylines:
        polMunicipio = sf.GetBoundMunicipio(cidade, uf)
        polMunicipioAreasUrbanizadas = sf.FiltrarAreasUrbanizadasPorMunicipio(
            cidade, uf
        )
        cache_polylines = [f"{cidade}-{uf}", polMunicipio, polMunicipioAreasUrbanizadas]
        cb.cCacheBoundingBox.areas_urbanas.add_polyline(chave_regiao, cache_polylines)
    else:
        wLog(f"Áreas urbanizadas e município recuperados do cache - {cidade} - {uf}")
        polMunicipio = cache_polylines[1]
        polMunicipioAreasUrbanizadas = cache_polylines[2]
    return polMunicipio, polMunicipioAreasUrbanizadas


################################################################################
def RouteCompAbrangencia(
    data: dict,
    user: str,
    pontoinicial: list,
    cidade: str,
    uf: str,
    escopo: str,
    distanciaPontos: int,
    regioes: list,
):
    """Processa rota do tipo compromisso de abrangência

    Args:
        data (dict): Dados do formulário.
        user (str): Nome do usuário.
        pontoinicial (list): Coordenadas do ponto inicial.
        cidade (str): Nome da cidade.
        uf (str): Sigla do estado.
        escopo (str): Escopo da rota.
        distanciaPontos (int): Distância entre os pontos.
        regioes (list): Lista de regiões.

    Returns:
        tuple: Arquivos de saída (mapa, mapa estático, KML).
    """

    UserData.nome = user
    UserData.AlgoritmoOrdenacaoPontos = data["AlgoritmoOrdenacaoPontos"]
    UserData.RaioDaEstacao = data["RaioDaEstacao"]
    UserData.GpsProximoPonto = data["GpsProximoPonto"]

    # wLog("GetBoundMunicipio e FiltrarAreasUrbanizadasPorMunicipio")

    polMunicipio, polMunicipioAreasUrbanizadas = get_areas_urbanas_cache(cidade, uf)

    gi.cGuiOutput.limits = polMunicipio
    gi.cGuiOutput.urbanAreas = polMunicipioAreasUrbanizadas

    match escopo:
        case "AreasUrbanizadas":
            pontosvisita = GeneratePointsWithinCity(
                polMunicipioAreasUrbanizadas, regioes, distanciaPontos
            )
        case "Municipio":
            pontosvisita = GeneratePointsWithinCity(
                polMunicipio, regioes, distanciaPontos
            )
        case _:
            raise ValueError(f"Escopo '{escopo}' não é válido.")

    regioes = AtualizaRegioesBoudingBoxPontosVisita(regioes, pontoinicial, pontosvisita)
    si.PreparaServidorRoteamento(regioes)
    RouteDetail = ClRouteDetailList()
    RouteDetail.pontoinicial = pontoinicial

    wLog("Desenhando Comunidades, Areas Urbanizadas e Município:")
    RouteDetail = ServerSetupJavaScript(RouteDetail)
    RouteDetail.mapcode += "    const TipoRoute = 'CompAbrangencia';\n"

    polylinesComunidades = get_polyline_comunities(regioes)
    RouteDetail = DesenhaComunidades(
        RouteDetail, polylinesComunidades
    )  # RouteDetail = DesenhaComunidades(RouteDetail, regioes)
    # cWrJsOut.DesenhaComunidades(polylinesComunidades)

    RouteDetail = DesenhaMunicipioAreasUrbanizadas(
        RouteDetail, cidade, polMunicipioAreasUrbanizadas
    )
    RouteDetail = DesenhaMunicipio(RouteDetail, cidade, polMunicipio)

    wLog("Ordenando e processando Pontos de Visita:")

    pontosvisita = OrdenarPontos(pontosvisita, pontoinicial)
    RouteDetail = PlotaPontosVisita(RouteDetail, pontosvisita, [])

    RouteDetail = DesenhaRegioes(RouteDetail, regioes)
    # cWrJsOut.DesenhaRegioes(RouteDetail, regioes)

    RouteDetail.GeraMapPolylineCaminho()

    fileMap, fileNameStatic, fileKml = GeraArquivosSaida(RouteDetail, "CompAbrangencia")
    return fileMap, fileNameStatic, fileKml


################################################################################
def GeraArquivosSaida(RouteDetail, tipoServico):
    buf = TimeStringTmp()
    fileMap = f"WebRotas{tipoServico}{buf}.html"
    fileName = f"templates/{fileMap}"
    gm.GeraMapaLeaflet(fileName, RouteDetail)

    fileMapStatic = f"WebRotas{tipoServico}Static{buf}.html"
    fileNameStaticF = f"templates/{fileMapStatic}"
    gm.GeraMapaLeaflet(fileNameStaticF, RouteDetail, static=True)

    fileKml = f"WebRotas{tipoServico}{buf}.kml"
    fileKmlF = f"templates/{fileKml}"
    # GerarKml(pontosvisita,fileKmlF)
    Gerar_Kml(RouteDetail.coordinates, RouteDetail.pontosvisitaDados, filename=fileKmlF)

    return fileMap, fileMapStatic, fileKml


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
    i = 0
    # [-22.88169706392197, -43.10262976730735,"P0","Local", "Descrição","Altitude","Ativo"],
    js_array = "[\n"
    for ponto in pontosvisitaDados:
        js_array += f'    [{ponto[0]}, {ponto[1]},"{ponto[2]}","{ponto[3]}", "{ponto[4]}","{ponto[5]}","Ativo"],\n'
        i = i + 1
    js_array = (
        js_array.rstrip(",\n") + "\n]"
    )  # Remover a última vírgula e adicionar fechamento

    # Criar a declaração completa
    js_code = '// Formato pontosvisitaDados - [-22.88169706392197, -43.10262976730735,"P0","Local", "Descrição","Altitude","Ativo"]\n'
    js_code = js_code + f"var pontosvisitaDados = {js_array};\n"
    return js_code


################################################################################
def PegaLinhaPontosVisitaDados(pontosvisitaDados, lat, lon):
    for linha in pontosvisitaDados:
        # wLog(f"linha - lat,lon - {lat},{lon} - {linha}")
        if linha[0] == lat and linha[1] == lon:
            return linha
    # wLog("PegaLinhaPontosVisitaDados - falhou")
    # wLog(f"linha - {linha}")
    return ""


################################################################################
def GeraPontosVisitaDados(pontosvisita):
    i = 0
    pontosvisitaDados = []
    for ponto in pontosvisita:
        lat, lon = ponto
        alt = 0
        dado = (lat, lon, f"P{i}", "Local", "", alt)
        pontosvisitaDados.append(dado)
        i = i + 1
    return pontosvisitaDados


################################################################################
def MesmaOrdenacaoPontosVisita(pontosvisitaDados, pontosvisita, new=False):
    pontosvisitaDadosNew = []
    i = 0
    for ponto in pontosvisita:
        latitude, longitude = ponto
        linha = PegaLinhaPontosVisitaDados(pontosvisitaDados, latitude, longitude)
        alt = 0
        if new:
            lin2 = linha[3]
            lin3 = linha[4]
        else:
            lin2 = linha[2]
            lin3 = linha[3]
        dado = (latitude, longitude, f"P{i}", lin2, lin3, alt)
        pontosvisitaDadosNew.append(dado)
        i = i + 1
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
    timeStp = get_formatted_timestamp()
    output = ""
    output += f"    var ListaRotasCalculadas = [];\n"
    output += f"    var bufdados = {{}};\n"
    output += f"    bufdados.id = 0;\n"
    output += f"    bufdados.time = '{timeStp}';\n"
    output += f"    bufdados.polylineRotaDat = [];\n"
    output += f"    bufdados.pontosvisitaDados = pontosvisitaDados;\n"
    output += f"    bufdados.pontosVisitaOrdenados = pontosVisitaOrdenados;\n"
    output += f"    bufdados.pontoinicial = [{RouteDetail.pontoinicial[0]},{RouteDetail.pontoinicial[1]},'{RouteDetail.pontoinicial[2]}'];\n"
    output += f"    bufdados.DistanceTotal = {RouteDetail.DistanceTotal / 1000};\n"
    output += f"    bufdados.rotaCalculada = 1;\n"  # Rota calculada pelo WebRotas
    output += f"    ListaRotasCalculadas.push(bufdados);\n"

    RouteDetail.append_mapcode(output)

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
def PegaAltitudesPVD_Batch(
    pontosvisitaDados,
):  # Batch faz chamadas em lote para o OpenElevation
    batch_size = 100
    for i in range(0, len(pontosvisitaDados), batch_size):
        batch = pontosvisitaDados[i : i + batch_size]
        altitudes = AltitudeOpenElevationBatch(batch, batch_size)
        for j in range(len(batch)):
            ponto = batch[j]
            lat, lon = ponto[0], ponto[1]
            alt = altitudes[j]
            pontosvisitaDados[i + j] = (lat, lon, ponto[2], ponto[3], ponto[4], alt)

    return pontosvisitaDados


################################################################################
def PlotaPontosVisita(RouteDetail, pontosvisita, pontosvisitaDados):
    wLog("PlotaPontosVisita - gerando rotas entre os pontos")
    i = 0
    RouteDetail.append_mapcode(f"    var RaioDaEstacao = {UserData.RaioDaEstacao};\n")
    RouteDetail.append_mapcode(
        f"    var GpsProximoPonto = '{UserData.GpsProximoPonto}';\n"
    )
    RouteDetail.append_mapcode(f"    var pontosVisitaOrdenados = [\n")

    for ponto in pontosvisita:
        latitude, longitude = ponto
        if i == len(pontosvisita) - 1:  # Verifica se é o último elemento
            RouteDetail.append_mapcode(f"       [{latitude}, {longitude}]")
        else:
            RouteDetail.append_mapcode(f"       [{latitude}, {longitude}],")
        i = i + 1

    RouteDetail.append_mapcode(f"    ];\n")

    if pontosvisitaDados != []:
        pontosvisitaDados = MesmaOrdenacaoPontosVisita(
            pontosvisitaDados, pontosvisita, new=False
        )
        pontosvisitaDados = PegaAltitudesPVD_Batch(
            pontosvisitaDados
        )  # Batch faz chamadas em lote para o OpenElevation

    else:
        pontosvisitaDados = GeraPontosVisitaDados(pontosvisita)
        pontosvisitaDados = MesmaOrdenacaoPontosVisita(
            pontosvisitaDados, pontosvisita, new=True
        )
        pontosvisitaDados = PegaAltitudesPVD_Batch(
            pontosvisitaDados
        )  # Batch faz chamadas em lote para o OpenElevation

    RouteDetail.append_mapcode(DeclaracaopontosvisitaDadosJS(pontosvisitaDados))

    gi.cGuiOutput.pontosvisitaDados = pontosvisitaDados
    RouteDetail.pontosvisitaDados = pontosvisitaDados

    RouteDetail.append_mapcode(
        f"    map.fitBounds(L.latLngBounds(pontosVisitaOrdenados));\n"
    )

    # RouteDetail.pontoinicial
    lat = RouteDetail.pontoinicial[0]
    lon = RouteDetail.pontoinicial[1]
    desc = RouteDetail.pontoinicial[2]

    RouteDetail.append_mapcode(
        f"         mrkPtInicial = L.marker([{lat}, {lon}]).addTo(map).setIcon(createSvgIconColorAltitude('i',10000));\n"
    )
    RouteDetail.append_mapcode(
        f"         mrkPtInicial.bindTooltip('{desc}', {{permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'}});\n"
    )

    ##############################################
    # Calcula rota entre os pontos os pontos a serem visitados
    (latf, lonf) = pontosvisita[0]
    RouteDetail = GenerateRouteMap(
        RouteDetail, lat, lon, latf, lonf
    )  # Faz a primeira rota saindo do ponto inicial ao primeiro ponto de visita

    i = 0
    RouteDetail.append_mapcode("var markerVet = [];")
    for ponto in pontosvisita:
        lat, lon = ponto

        # altitude = AltitudeAnatelServer(lat,lon)
        altitude = AltitudePontoVisita(pontosvisitaDados, lat, lon)
        Descricao = DescricaoPontoVisita(pontosvisitaDados, lat, lon)

        RouteDetail.append_mapcode(
            f"         markerbufTemp = L.marker([{lat}, {lon}]).addTo(map).on('click', onMarkerClick).setIcon(createSvgIconColorAltitude({i},{altitude}));\n"
        )
        RouteDetail.append_mapcode(
            f"         markerbufTemp._icon.setAttribute('data-id', '{i}'); markerbufTemp._icon.setAttribute('clicado', '0'); markerbufTemp._icon.setAttribute('tamanho', 'full'); markerbufTemp._icon.setAttribute('altitude', '{altitude}');\n"
        )
        RouteDetail.append_mapcode(
            f"         markerbufTemp.bindTooltip('Altitude: {altitude}<br>{Descricao}', {{permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'}});\n"
        )
        RouteDetail.append_mapcode(f"         markerVet.push(markerbufTemp);\n")

        if i == 0:
            (latfI, lonfI) = pontosvisita[i]
        if i == (len(pontosvisita) - 1):
            (latfF, lonfF) = pontosvisita[i]
        if i > 0:
            (lati, loni) = pontosvisita[i - 1]
            (latf, lonf) = pontosvisita[i]
            RouteDetail = GenerateRouteMap(RouteDetail, lati, loni, latf, lonf)
        i = i + 1
    # ----------------------------------------------------------------------
    gi.cGuiOutput.waypoints_route = RouteDetail.coordinates
    gi.cGuiOutput.estimated_distance = RouteDetail.DistanceTotal
    # ----------------------------------------------------------------------
    RouteDetail.DeclaraArrayRotas()
    RouteDetail.append_mapcode(
        "           const defaultIcon = markerVet[1].getIcon();\n"
    )
    return RouteDetail


################################################################################
def adjust_pontosvisitadados(pontosvisita, pontosvisitaDados):
    if pontosvisitaDados != []:
        pontosvisitaDados = MesmaOrdenacaoPontosVisita(
            pontosvisitaDados, pontosvisita, new=False
        )
        pontosvisitaDados = PegaAltitudesPVD_Batch(
            pontosvisitaDados
        )  # Batch faz chamadas em lote para o OpenElevation

    else:
        pontosvisitaDados = GeraPontosVisitaDados(pontosvisita)
        pontosvisitaDados = MesmaOrdenacaoPontosVisita(
            pontosvisitaDados, pontosvisita, new=True
        )
        pontosvisitaDados = PegaAltitudesPVD_Batch(
            pontosvisitaDados
        )  # Batch faz chamadas em lote para o OpenElevation
    return pontosvisitaDados


################################################################################
def PlotaPontosVisitaNoJS(RouteDetail, pontosvisita, pontosvisitaDados):
    # ----------------------------------------------------------------------
    pontosvisitaDados = adjust_pontosvisitadados(pontosvisita, pontosvisitaDados)
    gi.cGuiOutput.pontosvisitaDados = pontosvisitaDados
    # ----------------------------------------------------------------------
    RouteDetail.pontosvisitaDados = pontosvisitaDados
    lat = RouteDetail.pontoinicial[0]
    lon = RouteDetail.pontoinicial[1]

    # Calcula rota entre os pontos os pontos a serem visitados
    RouteDetail = GenerateRouteMap(RouteDetail)

    (latf, lonf) = pontosvisita[0]
    RouteDetail = GenerateRouteMap(
        RouteDetail, lat, lon, latf, lonf
    )  # Faz a primeira rota saindo do ponto inicial ao primeiro ponto de visita

    i = 0
    for ponto in pontosvisita:
        lat, lon = ponto

        if i == 0:
            (latfI, lonfI) = pontosvisita[i]
        if i == (len(pontosvisita) - 1):
            (latfF, lonfF) = pontosvisita[i]
        if i > 0:
            (lati, loni) = pontosvisita[i - 1]
            (latf, lonf) = pontosvisita[i]
            RouteDetail = GenerateRouteMap(RouteDetail, lati, loni, latf, lonf)
        i = i + 1
    # ----------------------------------------------------------------------
    gi.cGuiOutput.waypoints_route = RouteDetail.coordinates
    gi.cGuiOutput.estimated_distance = RouteDetail.DistanceTotal
    # ----------------------------------------------------------------------
    return RouteDetail


################################################################################
def PegaPontosVisita(pontosvisitaDados):
    pontosvisita = []
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
            return ponto[5]  # Retorna o campo de altitude (5º elemento)
    return "Endereço não encontrado para a latitude e longitude fornecidas."


################################################################################
def RoteamentoOSMR(username, porta, pontosvisita, pontoinicial, recalcularrota):
    UserData.nome = username
    UserData.OSMRport = porta
    RouteDetail = ClRouteDetailList()
    # Calcula trecho de roto do pontoinicial ao primeiro ponto de visita
    (latfI, lonfI) = pontosvisita[0]
    wLog(f"RoteamentoOSMR - pontosvisita[0] {latfI},{lonfI}", level="debug")
    # wLog(f"RoteamentoOSMR - pontoinicial {pontoinicial[0]},{pontoinicial[1]}",level="debug")
    # wLog("Pontos de Visita antes ordenação:",level="debug")
    # for ponto in pontosvisita:
    #     wLog(f"Latitude: {ponto[0]}, Longitude: {ponto[1]}",level="debug")

    if recalcularrota == 1:
        wLog(f"Reordenando pontos de visita", level="debug")
        pontosvisita = OrdenarPontosDistanciaOSMRMultiThread(pontosvisita, pontoinicial)

    # wLog("Pontos de Visita apos ordenação:",level="debug")
    # for ponto in pontosvisita:
    #     wLog(f"Latitude: {ponto[0]}, Longitude: {ponto[1]}",level="debug")

    RouteDetail = GenerateRouteMap(
        RouteDetail, pontoinicial[0], pontoinicial[1], latfI, lonfI
    )

    for i in range(len(pontosvisita) - 1):
        lati, loni = pontosvisita[i]
        latf, lonf = pontosvisita[i + 1]
        RouteDetail = GenerateRouteMap(RouteDetail, lati, loni, latf, lonf)

    return RouteDetail.coordinates, RouteDetail.DistanceTotal, pontosvisita


################################################################################
def create_standard_cache(data):
    from flask import jsonify

    UserData.nome = "CacheCreator"
    wLog(
        "#############################################################################################"
    )
    wLog("Recebida solicitação criar cache das GR")
    for regiao in data["RegioesCache"]:
        gr_data = regiao
        estados_siglas = gr_data["SiglaEstado"]
        lista_municipios = gr_data["ListaMunicipios"]
        regioes = gr_data["regioes"]
        cb.cCacheBoundingBox.gr = gr_data["GR"] + "  " + ", ".join(gr_data["UO"])
        cb.cCacheBoundingBox.state = ", ".join(gr_data["SiglaEstado"])
        wLog(f"{cb.cCacheBoundingBox.gr} {cb.cCacheBoundingBox.state}")
        create_standard_cache_from_place(estados_siglas, lista_municipios, regioes)
        cb.cCacheBoundingBox.gr = "-"
        cb.cCacheBoundingBox.state = "-"

    cb.cCacheBoundingBox._schedule_save()
    wLog(
        "#############################################################################################"
    )
    return jsonify({"Info": f"Standard cache criado com sucesso"}), 400


################################################################################
def create_standard_cache_from_place(estados_siglas, lista_municipios, regioes):
    wLog(
        f"Calculando cache para os estados: {estados_siglas} e municípios: {lista_municipios}"
    )
    if not lista_municipios:
        bbox = sf.get_bounding_box_from_states(estados_siglas)
    else:
        bbox = sf.get_bounding_box_for_municipalities(lista_municipios)

    bbox = sf.expand_bounding_box(bbox, 50)  # 50 km de margem
    regioes = update_regions_bounding_box(bbox, regioes)
    si.PreparaServidorRoteamento(regioes)

    bounding_box = rg.extrair_bounding_box_de_regioes(regioes)
    polylinesComunidades = cb.cCacheBoundingBox.comunidades_cache.get_polylines(regioes)
    if not polylinesComunidades:
        polylinesComunidades = sf.FiltrarComunidadesBoundingBox(bounding_box)
        cb.cCacheBoundingBox.comunidades_cache.add_polyline(
            regioes, polylinesComunidades
        )


################################################################################
def update_regions_bounding_box(bbox, regioes):

    NewRegioes = []

    box = bbox
    regioesglobal = {"name": "boundingBoxRegion", "coord": box}
    NewRegioes.append(regioesglobal)
    for regiao in regioes:
        nome = regiao.get("nome", "SemNome").replace(" ", "_")
        coordenadas = regiao.get("coord", [])
        regiaook = {"name": nome, "coord": coordenadas}
        NewRegioes.append(regiaook)

    if cb.cCacheBoundingBox.get_cache(NewRegioes) is not None:
        NewRegioes = cb.cCacheBoundingBox.get_cache(NewRegioes)

    return NewRegioes


################################################################################
def RoutePontosVisita(data, user, pontoinicial, pontosvisitaDados, regioes):
    UserData.nome = user
    UserData.AlgoritmoOrdenacaoPontos = data["AlgoritmoOrdenacaoPontos"]
    UserData.RaioDaEstacao = data["RaioDaEstacao"]
    UserData.GpsProximoPonto = data["GpsProximoPonto"]

    pontosvisita = PegaPontosVisita(pontosvisitaDados)
    regioes = AtualizaRegioesBoudingBoxPontosVisita(regioes, pontoinicial, pontosvisita)
    si.PreparaServidorRoteamento(regioes)
    RouteDetail = ClRouteDetailList()
    RouteDetail.pontoinicial = pontoinicial

    wLog("Desenhando Comunidades:")
    RouteDetail = ServerSetupJavaScript(RouteDetail)
    RouteDetail.mapcode += f"    const TipoRoute = 'PontosVisita';\n"

    polylinesComunidades = get_polyline_comunities(regioes)
    RouteDetail = DesenhaComunidades(
        RouteDetail, polylinesComunidades
    )  # RouteDetail = DesenhaComunidades(RouteDetail, regioes)
    # cWrJsOut.DesenhaComunidades(polylinesComunidades)

    # Processa Pontos de Visita
    wLog(f"Ordenando e processando Pontos de Visita: ")
    pontosvisita = OrdenarPontos(pontosvisita, pontoinicial)

    RouteDetail = PlotaPontosVisita(RouteDetail, pontosvisita, pontosvisitaDados)
    RouteDetail = DesenhaRegioes(RouteDetail, regioes)
    wo.cWrJsOut.DesenhaRegioes(RouteDetail, regioes)
    RouteDetail.GeraMapPolylineCaminho()

    # servidor temp     python3 -m http.server 8080
    #
    fileMap, fileNameStatic, fileKml = GeraArquivosSaida(RouteDetail, "PontosVisita")
    return fileMap, fileNameStatic, fileKml


###########################################################################################################################
def AtualizaRegioesBoudingBoxPontosVisita(regioes, pontoinicial, pontosvisita):

    lat_min, lat_max, lon_min, lon_max = calcula_bounding_box_pontos(
        pontoinicial, pontosvisita, margem_km=50
    )
    NewRegioes = []

    box = [
        [lat_max, lon_min],
        [lat_max, lon_max],
        [lat_min, lon_max],
        [lat_min, lon_min],
    ]
    regioesglobal = {"name": "boundingBoxRegion", "coord": box}

    gi.cGuiOutput.pontoinicial = pontoinicial
    gi.cGuiOutput.bounding_box = box
    NewRegioes.append(regioesglobal)
    for regiao in regioes:
        nome = regiao.get("nome", "SemNome").replace(" ", "_")
        coordenadas = regiao.get("coord", [])
        regiaook = {"name": nome, "coord": coordenadas}
        NewRegioes.append(regiaook)

    if cb.cCacheBoundingBox.get_cache(NewRegioes) is not None:
        NewRegioes = cb.cCacheBoundingBox.get_cache(NewRegioes)

    return NewRegioes


###########################################################################################################################
def calcula_bounding_box_pontos(pontoinicial, pontos, margem_km=50):
    """
    Calcula um bounding box expandido em torno de um grupo de pontos, incluindo um ponto inicial.

    Args:
        pontoinicial (tuple): Coordenadas do ponto inicial (lat, lon).
        pontos (list): Lista de coordenadas [(lat, lon), ...].
        margem_km (float): Margem adicional em km ao redor do grupo de pontos.

    Returns:
        dict: Limites do bounding box (lat_min, lat_max, lon_min, lon_max).
    """
    if not pontos:
        raise ValueError("A lista de pontos não pode estar vazia.")

    # Inclui o ponto inicial na lista de pontos
    todos_pontos = pontos + [pontoinicial]

    # Determina os limites mínimos e máximos de latitude e longitude
    lat_min = min(p[0] for p in todos_pontos)
    lat_max = max(p[0] for p in todos_pontos)
    lon_min = min(p[1] for p in todos_pontos)
    lon_max = max(p[1] for p in todos_pontos)

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

    return lat_min, lat_max, lon_min, lon_max


###########################################################################################################################
def RouteContorno(
    data, user, pontoinicial, central_point, regioes, radius_km=5, num_points=8
):
    UserData.nome = user
    UserData.AlgoritmoOrdenacaoPontos = data["AlgoritmoOrdenacaoPontos"]
    UserData.RaioDaEstacao = data["RaioDaEstacao"]
    UserData.GpsProximoPonto = data["GpsProximoPonto"]

    # Coordenadas da rota (exemplo de uma rota circular simples)

    pontosvisita = GeneratePointsAround(
        latitude=central_point[0],
        longitude=central_point[1],
        radius_km=radius_km,
        num_points=num_points,
    )

    regioes = AtualizaRegioesBoudingBoxPontosVisita(regioes, pontoinicial, pontosvisita)

    si.PreparaServidorRoteamento(regioes)

    RouteDetail = ClRouteDetailList()
    RouteDetail.pontoinicial = pontoinicial

    wLog("Desenhando Comunidades:")
    RouteDetail = ServerSetupJavaScript(RouteDetail)

    RouteDetail.append_mapcode(f"    const TipoRoute = 'DriveTest';\n")

    polylinesComunidades = get_polyline_comunities(regioes)
    # RouteDetail = DesenhaComunidades(RouteDetail, polylinesComunidades) # RouteDetail = DesenhaComunidades(RouteDetail, regioes)
    RouteDetail.DesenhaComunidades(polylinesComunidades)

    # Criar um mapa centrado no ponto central
    # RouteDetail.mapcode += f"    const map = L.map('map').setView([{central_point[0]}, {central_point[1]}], 13);\n"
    RouteDetail.append_mapcode(
        f"     map.setView([{central_point[0]}, {central_point[1]}], 13);\n"
    )

    # Adicionar uma marca no ponto central
    RouteDetail.append_mapcode(
        f"    var markerCentral = L.marker([{central_point[0]}, {central_point[1]}]).addTo(map); \n"
    )
    RouteDetail.append_mapcode(
        f"    markerCentral.bindTooltip('Ponto Central', {{permanent: false,direction: 'top',offset: [0, -60],className:'custom-tooltip'}});\n"
    )
    RouteDetail.append_mapcode("     markerCentral.setIcon(iMarquerVerde);\n")

    pontosvisita = OrdenarPontos(pontosvisita, pontoinicial)

    # ---------------------
    # Parei aqui

    # RouteDetail = PlotaPontosVisitaNoJS(RouteDetail, pontosvisita, [])
    RouteDetail = PlotaPontosVisita(RouteDetail, pontosvisita, [])

    RouteDetail.DesenhaRegioes(regioes)

    RouteDetail.GeraMapPolylineCaminho()
    # GerarKml(coordenadasrota, filename="rota.kml")

    # servidor temp     python3 -m http.server 8080
    #
    fileMap, fileNameStatic, fileKml = GeraArquivosSaida(RouteDetail, "Contorno")
    return fileMap, fileNameStatic, fileKml


###########################################################################################################################
def main():
    return


###########################################################################################################################
if __name__ == "__main__":
    main()
###########################################################################################################################
