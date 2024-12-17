import os
import WebRota as wr
import datetime
from flask import Flask,render_template,request, jsonify, send_file # pip install flask
from flask_compress import Compress  # pip install flask_compress
from flask_cors import CORS # pip install flask-cors

  # pip install flask
# estudar como melhorar a escalabilidade com gunicorn

# gunicorn -w 4 -b 0.0.0.0:8000 Site:app
# Como instalar o gunicorn no ningx docker

# ngrok http 5001 

wr.FileLog=os.getcwd()+"\logs\WebRotasServer.log"
print(f"Arquivo de log: {wr.FileLog}")

app = Flask(__name__, static_folder='static')
CORS(app)  # Habilita CORS para todas as rotas
Compress(app)

# Configuração para forçar a recarga de arquivos estáticos
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Ativa o auto-reload dos templates

################################################################################
@app.route('/recebe<ip>.html', methods=['POST','GET'])   # exemplo /recebe<18.64.207.107>.html 
def SaveIp(ip):
    # htm.GetGeolocation(ip)
    return "ok"
################################################################################
@app.route('/')                # return render_template('index.html')
def index():
    id = request.args.get('news') # parametro news da url
    return # htm.GeraPaginaBlog(id)
################################################################################
@app.route('/ok', methods=['GET'])
def ok():
    return "ok"
################################################################################
@app.route('/map/<filename>')
def mapa_leaflet(filename):
    template_file = filename
    try:
        # Renderiza o template com o nome do arquivo fornecido
        return render_template(template_file)
    except Exception as e:
        # Retorna uma mensagem de erro caso o template não seja encontrado
        return f"Erro: {e}", 404
################################################################################
# URL do servidor OSRM 
import requests
@app.route("/route", methods=["GET"])
def get_route():
    """
    Rota Flask que envia requisições para o servidor OSRM e retorna a resposta.
       curl "http://127.0.0.1:5001/route?porta=50001&start=-46.6388,-23.5489&end=-46.6253,-23.5339"

      
    """
    # Parâmetros da requisição (origem e destino)
    start = request.args.get("start")  # Formato esperado: "lon,lat"
    end = request.args.get("end")      # Formato esperado: "lon,lat"
    porta = request.args.get("porta")
    OSRM_SERVER_URL = f"http://127.0.0.1:{porta}"  # Exemplo local
    
    if not start or not end or not porta:
        return jsonify({"error": "Os parâmetros 'start' e 'end' são obrigatórios"}), 400

    try:
        # Construir a URL para a requisição ao OSRM
        osrm_url = f"{OSRM_SERVER_URL}/route/v1/driving/{start};{end}?overview=full&geometries=polyline&steps=true"

        # Requisição ao servidor OSRM
        osrm_response = requests.get(osrm_url)
        osrm_response.raise_for_status()  # Verifica se houve erro na requisição

        # Retorna a resposta JSON do OSRM para o cliente Flask
        return jsonify(osrm_response.json())

    except requests.RequestException as e:
        return jsonify({"error": f"Falha na comunicação com o servidor OSRM: {str(e)}"}), 500
################################################################################
import multiprocessing
import json
################################################################################
def SalvaDataArq(data):   
    # Salva os dados em um arquivo com o nome do usuário
    user=data["User"]
    try:
        file_name = f"{user}.json"
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
                
        print(f"Dados salvos com sucesso no arquivo: {file_name}")           
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")
        return jsonify({"error": "Erro ao salvar os dados"}), 500
################################################################################
# pyinstaller --onefile --add-data "C:\\Users\\andre\\miniconda3\\envs\\webrotas/Lib/site-packages/flask;flask" Server.py
################################################################################
def ProcessaRequisicoesAoServidor(data):
  wr.wLog("Executando em paralelo requisição ao servidor")
  with app.app_context():
    #---------------------------------------------------------------------------------------------
    TipoReq = data["TipoRequisicao"]
    if TipoReq=="DriveTest":
       # Obtém valores do JSON
           # Verifica se todos os campos necessários estão presentes

       print("\n\n#############################################################################################")
       print("Recebida solicitação de drivetest\n")
       if not all(key in data for key in ("latitude", "longitude", "raio")):
          return jsonify({"error": "Campos latitude, longitude e raio são necessários"}), 400
      
       user=data["User"]
       
       latitude = data["latitude"]
       longitude = data["longitude"]
       raio = data["raio"]
       regioes = data.get("regioes", []) 
       # Processa os dados (exemplo: exibe no console)
       print(f"Latitude: {latitude}, Longitude: {longitude}, Raio: {raio}")
       central_point = [latitude, longitude] 
       fileName,fileNameStatic,fileKml=wr.RouteDriveTest(user,central_point,regioes,radius_km=raio)
       # Retorna uma resposta de confirmação
       return jsonify({"MapaOk": fileName,"Url":f"http://127.0.0.1:5001/map/{fileName}",
                       "HtmlStatic":f"http://127.0.0.1:5001/download/{fileNameStatic}",
                       "Kml":f"http://127.0.0.1:5001/download/{fileKml}"}
                      ), 200
    #---------------------------------------------------------------------------------------------
    TipoReq = data["TipoRequisicao"]
    if TipoReq=="PontosVisita":
       # Obtém valores do JSON
       print("\n\n#############################################################################################")
       print("Recebida solicitação pontos de visita\n")
       if not all(key in data for key in ("pontosvisita", "regioes")):
          return jsonify({"error": "Campos pontosvisita, regioes são necessários"}), 400
      
       user=data["User"]
       pontosvisita = data.get("pontosvisita", [])   
       regioes = data.get("regioes", []) 

       # Processa os dados (exemplo: exibe no console)
       print(f"pontosvisita: {pontosvisita},  Regiões Evitar: {regioes}")
       fileName,fileNameStatic,fileKml=wr.RoutePontosVisita(user,pontosvisita,regioes)
       # Retorna uma resposta de confirmação
       return jsonify({"MapaOk": fileName,"Url":f"http://127.0.0.1:5001/map/{fileName}",
                       "HtmlStatic":f"http://127.0.0.1:5001/download/{fileNameStatic}",
                       "Kml":f"http://127.0.0.1:5001/download/{fileKml}"}
                      ), 200
    #---------------------------------------------------------------------------------------------
    TipoReq = data["TipoRequisicao"]
    if TipoReq=="Abrangencia":
       # Obtém valores do JSON
       print("\n\n#############################################################################################")
       print("Recebida solicitação de compromisso de abrangência\n")
       # https://informacoes.anatel.gov.br/legislacao/procedimentos-de-fiscalizacao/1724-portaria-2453
       if not all(key in data for key in ("cidade", "distancia_pontos", "regioes")):
          return jsonify({"error": "Campos cidade, distancia_pontos e regioes são necessários"}), 400
      
       user=data["User"]
       cidade = data["cidade"]
       uf = data["uf"]
       distanciaPontos = data["distancia_pontos"]
       regioes = data["regioes"]

       # Processa os dados (exemplo: exibe no console)
       print(f"Cidade: {cidade},Uf: {uf}, distancia_pontos: {distanciaPontos} m, Regiões Evitar: {regioes}")
       fileName,fileNameStatic,fileKml=wr.RouteCompAbrangencia(user,cidade,uf,distanciaPontos,regioes)
       # Retorna uma resposta de confirmação
       return jsonify({"MapaOk": fileName,"Url":f"http://127.0.0.1:5001/map/{fileName}",
                       "HtmlStatic":f"http://127.0.0.1:5001/download/{fileNameStatic}",
                       "Kml":f"http://127.0.0.1:5001/download/{fileKml}"}
                      ), 200
    #---------------------------------------------------------------------------------------------    
    return jsonify({"ErroPedido": "ErroPedido"}), 200
################################################################################
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=40)
ListaTarefas = []
################################################################################
@app.route('/download/<filename>')
def download_file(filename):
    # Caminho absoluto ou relativo para o arquivo
    caminho_arquivo = f"templates/{filename}"
    try:
        return send_file(caminho_arquivo, as_attachment=True)
    except Exception as e:
        return f"Erro ao enviar o arquivo: {e}"
################################################################################    
@app.route('/webrotas', methods=['POST'])
def process_location():
    # Obtém o JSON da requisição
    data = request.get_json()
    
    return ProcessaRequisicoesAoServidor(data) 
    
    """"
    if not (key in data for key in ("TipoRequisicao")):
       return jsonify({"error": "Tipo requisicao: 'TipoRequisicao' nao informado."}), 400
    user=data["User"]
    tiporequisicao=data["TipoRequisicao"]
    
    for dado in ListaTarefas:
       if dado[0] == user and dado[1] == tiporequisicao:
            if dado[2].done():
                ret = dado[2].result()
                ListaTarefas.remove(dado)
                return ret
            if dado[2].running():
                return jsonify({"Tarefa em execucao": "OK"}), 202
    
    # Usando executor para processar a requisição em uma thread separada
    future = executor.submit(ProcessaRequisicoesAoServidor, data)
    ListaTarefas.append([user,tiporequisicao,future])
    # Aguardar até que a tarefa seja concluída e acessar o resultado
    # result = future.result()  # Esse comando vai bloquear até a execução da tarefa ser concluída
    """ 
    return jsonify({"Tarefa em execucao": "OK"}), 202
################################################################################
if __name__ == '__main__':
    app.run(debug=True,port=5001)
################################################################################
