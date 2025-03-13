import os
import sys

# Caminho relativo da pasta "tests" para "webdir"
relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "backend", "webdir"))
# Adiciona o caminho ao sys.path
sys.path.append(relative_path)

import client as cl


payload = {
    "User": "Fabio",
    "TipoRequisicao": "Abrangencia",
    "PontoInicial": [-23.587577163638976, -46.63326070110086,"Anatel São Paulo"],            
    "RaioDaEstacao": 200,            # distância em metros para estação/ponto do mapa ser considerada visitada - null - nunca
    "GpsProximoPonto": "ProximoDaRota",           # "ProximoDaRota", "MaisProximo" - próximo ponto da rota a ser selecionada pelo GPS
    "Escopo":"AreasUrbanizadas",                   # Opções: "Municipio" ou "AreasUrbanizadas" 
    "cidade": "São Paulo",
    "uf": "SP",
    "AlgoritmoOrdenacaoPontos": "DistanciaOSMRMultiThread",     #  "DistanciaGeodesica","DistanciaOSMR", "DistanciaOSMRMultiThread", "Nenhuma"
    "distancia_pontos": "3000",  # distancia entre pontos em metros
    "regioes": ""
}
cl.enviar_json(payload, "http://localhost:5001/webrotas")