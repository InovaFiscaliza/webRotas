import requests
import webbrowser
###########################################################################################################################
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
###########################################################################################################################