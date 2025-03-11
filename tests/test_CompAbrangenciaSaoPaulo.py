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
enviar_json(payload, "http://localhost:5001/webrotas")