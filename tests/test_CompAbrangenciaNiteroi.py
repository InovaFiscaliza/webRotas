import requests
import webbrowser


##################################################################################################
def enviar_json(payload, url):
    # Envia uma requisição POST com o JSON para o URL especificado
    try:
        response = requests.post(url, json=payload)
        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            print("-----------------------------------------------")
            print("Requisição bem-sucedida:")
            print(response.json())
            print("-----------------------------------------------")
            url = response.json().get("Url", None)
            if url:
               webbrowser.open(url)
        else:
            print(f"Erro {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print("Erro na requisição:", e)
##################################################################################################


payload = {
    "User": "Fabio",
    "TipoRequisicao": "Abrangencia",
    "PontoInicial": [-22.90236790344037, -43.17420024484698,"Anatel Rio de Janeiro"],            
    "RaioDaEstacao": 200,            # distância em metros para estação/ponto do mapa ser considerada visitada - null - nunca
    "GpsProximoPonto": "ProximoDaRota",           # "ProximoDaRota", "MaisProximo" - próximo ponto da rota a ser selecionada pelo GPS
    "Escopo":"AreasUrbanizadas",                   # Opções: "Municipio" ou "AreasUrbanizadas" 
    "cidade": "Niterói",
    "uf": "RJ",
    "AlgoritmoOrdenacaoPontos": "DistanciaOSMRMultiThread",     #  "DistanciaGeodesica","DistanciaOSMR", "DistanciaOSMRMultiThread", "Nenhuma"
    "distancia_pontos": "1600",  # distancia entre pontos em metros
    "regioes": ""
}
enviar_json(payload, "http://localhost:5001/webrotas")