import os
import sys

# Caminho relativo da pasta "tests" para "webdir"
relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "backend", "webdir"))
# Adiciona o caminho ao sys.path
sys.path.append(relative_path)

import client as cl


regioesBuf =  [       
        {
            "nome": "!Jacare",
            "coord": [
                [-22.918740407473486, -43.046581350886925],
                [-22.91621425399815, -43.03460034948952],
                [-22.93363046037466, -43.038786482507895],
                [-22.93030692975052, -43.04441610967053],
                [-22.926717425070326, -43.05177792980626],                
                [-22.918341544265797, -43.04383871201282]
            ]
        },
        {
            "nome": "!Parque da Cidade",
            "coord": [
                [-22.920468800811552, -43.09392796446328],
                [-22.92139946519323, -43.08829833730066],
                [-22.9233937244859, -43.08238001130917],
                [-22.929908100265653, -43.07862692653409],
                [-22.93628922581668, -43.08468960194],                
                [-22.93602335158884, -43.09768104923836]
            ]
        },
        {
            "nome": "!Outra",
            "coord": [
                [-22.87731577172224, -43.09040921338159],   
                [-22.880204254693243, -43.0450646121466],     
                [-22.908733527841232, -43.05294065586869],      
                [-22.90788830229889, -43.092856139586516]

            ]
        }        
    ]
    

payload = {
    "User": "Andre",
    "TipoRequisicao": "Contorno",
    "PontoInicial": [-22.90236790344037, -43.17420024484698,"Anatel Rio de Janeiro"],            # Anatel Rio de Janeiro -22.90236790344037, -43.17420024484698
    "RaioDaEstacao": 200,            # distância em metros para estação/ponto do mapa ser considerada visitada - null - nunca
    "GpsProximoPonto": "ProximoDaRota",           # "ProximoDaRota", "MaisProximo" - próximo ponto da rota a ser selecionada pelo GPS
    "latitude": -22.910555413451096,        
    "longitude": -43.16360553394545,
    "raio": 10,
    "numeropontos":21,
    "AlgoritmoOrdenacaoPontos": "DistanciaOSMRMultiThread",     #  "DistanciaGeodesica","DistanciaOSMR", "DistanciaOSMRMultiThread", "Nenhuma" 
    "regioes": regioesBuf
}


cl.enviar_json(payload, "http://localhost:5001/webrotas")