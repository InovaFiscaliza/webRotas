#!/usr/bin/env python3
"""
Provê servidor web para cálculo de rotas.

:args:
    --port: Porta para o servidor Flask (default: 5001)
    --debug: Ativa modo de debug (default: False)
"""

import sys
import json
import requests
import argparse
from unidecode import unidecode

from flask import (
    Flask,
    Response,
    render_template,
    jsonify,
    send_file,
    send_from_directory,
    request,
    redirect
) 
from flask_compress import Compress
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

import webRota as wr
import server_env as se
import routing_servers_interface as rsi
import CacheBoundingBox as cb
import GuiOutput as gi

################################################################################
""" Variáveis globais """

REQUIRED_KEYS = {
    "Contorno":       { "latitude", "longitude", "raio" },
    "PontosVisita":   { "pontosvisita" },
    "Abrangencia":    { "cidade", "uf", "Escopo", "distancia_pontos" },
    "RoteamentoOSMR": { "PortaOSRMServer"}
}

env = se.ServerEnv()

################################################################################
# TODO #4 Use standard paths defined in a configuration section or file. May use ProgramData/Anatel/WebRotas, as other applications from E!, where ProgramData folder should use system variables.

wr.log_filename = env.log_file
wr.wLog(f"Arquivo de log: {env.log_file}")

app = Flask(__name__, static_folder="static", static_url_path="/webRotas")
CORS(app)  # Habilita CORS para todas as rotas
Compress(app)
# Configuração para forçar a recarga de arquivos estáticos
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True  # Ativa o auto-reload dos templates

#-----------------------------------------------------------------------------------#
# INICIALIZAÇÃO
#-----------------------------------------------------------------------------------#
@app.route("/", methods=["GET"])
def _root():
    return redirect("/webRotas/index.html")

@app.route("/<path:filepath>", methods=["GET"])
def _static_files(filepath):
    return send_from_directory("static", filepath)

#-----------------------------------------------------------------------------------#
# PROCESSA REQUISIÇÃO, RETORNANDO ROTA AUTOMÁTICA
#-----------------------------------------------------------------------------------#
@app.route('/process', methods=['POST'])
def _process():
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "Invalid or missing sessionId"}), 400
    gi.cGuiOutput.session_id = session_id
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400
    
    # with open("../../../tests/routing3.json", "r") as f:
    #     json_string = f.read()
    
    ProcessaRequisicoesAoServidor(data)
    json_string = gi.cGuiOutput.criar_json_routing()
    return Response(json_string, mimetype='application/json')

#-----------------------------------------------------------------------------------#
# REPROCESSA REQUISIÇÃO, RETORNANDO ROTA CUSTOMIZADA
#-----------------------------------------------------------------------------------#
@app.route('/reprocess', methods=['POST'])
def _reprocess():
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "Invalid or missing sessionId"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    ProcessaRequisicoesAoServidor(data)
    json_string = gi.cGuiOutput.criar_json_routing()    
    # return jsonify({ "error": "Mensagem erro de teste" }), 500
    return Response(json_string, mimetype='application/json')

#-----------------------------------------------------------------------------------#
# OUTRAS ROTAS
#-----------------------------------------------------------------------------------#
@app.route("/ok", methods=["GET"])
def _ok():
    return "ok"

#-----------------------------------------------------------------------------------#
@app.route("/map/<filename>")
def mapa_leaflet(filename):
    template_file = filename
    try:
        # Renderiza o template com o nome do arquivo fornecido
        return render_template(template_file)
    except Exception as e:
        # Retorna uma mensagem de erro caso o template não seja encontrado
        return f"Erro: {e}", 404


#-----------------------------------------------------------------------------------#
# URL do servidor OSRM
@app.route("/route", methods=["GET"])
def get_route():
    """
    Rota Flask que envia requisições para o servidor OSRM e retorna a resposta.
       curl "http://127.0.0.1:5001/route?porta=5001&start=-46.6388,-23.5489&end=-46.6253,-23.5339"
    """
    # Parâmetros da requisição (origem e destino)
    start = request.args.get("start")  # Formato esperado: "lon,lat"
    end = request.args.get("end")  # Formato esperado: "lon,lat"
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
        return jsonify(
            {"error": f"Falha na comunicação com o servidor OSRM: {str(e)}"}
        ), 500


#-----------------------------------------------------------------------------------#
@app.route("/health", methods=["GET"])
def get_health():
    # Parâmetros da requisição (origem e destino)
    porta = request.args.get("porta")
    # http://localhost:50002/route/v1/driving/0,0;1,1?overview=false
    OSRM_SERVER_URL = f"http://127.0.0.1:{porta}"  # Exemplo local

    try:
        # Construir a URL para a requisição ao OSRM
        osrm_url = f"{OSRM_SERVER_URL}/route/v1/driving/0,0;1,1?overview=false"

        # Requisição ao servidor OSRM
        osrm_response = requests.get(osrm_url)
        osrm_response.raise_for_status()  # Verifica se houve erro na requisição

        # Retorna a resposta JSON do OSRM para o cliente Flask
        return jsonify(osrm_response.json())

    except requests.RequestException as e:
        return jsonify(
            {"error": f"Falha na comunicação com o servidor OSRM: {str(e)}"}
        ), 500

#-----------------------------------------------------------------------------------#
@app.route("/download/<filename>")
def download_file(filename):
    # Caminho absoluto ou relativo para o arquivo
    caminho_arquivo = f"templates/{filename}"
    try:
        return send_file(caminho_arquivo, as_attachment=True)
    except Exception as e:
        return f"Erro ao enviar o arquivo: {e}"

#-----------------------------------------------------------------------------------#
@app.route("/webrotas", methods=["POST"])
def process_location():
    # Obtém o JSON da requisição
    data = request.get_json()
    return ProcessaRequisicoesAoServidor(data)

################################################################################
def SalvaDataArq(data):
    # Salva os dados em um arquivo com o nome do usuário
    user = data["User"]
    try:
        file_name = f"{user}.json"
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        wr.wLog(f"Dados salvos com sucesso no arquivo: {file_name}")
    except Exception as e:
        wr.wLog(f"Erro ao salvar os dados: {e}")
        return jsonify({"error": "Erro ao salvar os dados"}), 500

###9

def default_points(radi:int) -> int:
    """Calcula o número de pontos padrão para a rota de contorno à partir do raio
    
    :param radi: Raio em metros
    :return: Número de pontos padrão
    """
    MIN_POINTS = 9
    POINTS_PER_KM = 2
    TWO_PI = 6.28318530718
    
    return max(MIN_POINTS, int(TWO_PI * radi * POINTS_PER_KM /1000))


################################################################################
# pyinstaller --onefile --add-data "C:\\Users\\andre\\miniconda3\\envs\\webrotas/Lib/site-packages/flask;flask" Server.py
################################################################################
def ProcessaRequisicoesAoServidor(data: dict) -> tuple:
    """Processa as requisições ao servidor WebRotas.
    
    :param data: Dicionário com os dados da requisição.
    :return: Tupla com a resposta da requisição e o código HTTP.
    """
    with app.app_context():
        try:
            request_type = data["TipoRequisicao"]
        except KeyError as e:
            return jsonify({"error": f"Campo TipoRequisicao não encontrado: {e}"}), 400
        
        if (request_type == "StandardCache"):
            return wr.create_standard_cache(data)
        
        if not REQUIRED_KEYS[request_type].issubset(data.keys()):
            return jsonify({"error": f"Campos necessários: {REQUIRED_KEYS[request_type]}"}), 400
        
        # set variables to arguments used in all types of requests
        user = unidecode(data.get("User", "Anatel"))
        regioes = data.get("regioes", [])
        pontoinicial = data.get("PontoInicial", [])
        # Nome do usuário para o log trancorrer com o nome correto o quanto antes sem o "none"
        wr.UserData.nome = user
        gi.cGuiOutput.requisition_data = data
        # Process the request according to the request type
        match request_type:
            case "Contorno":
                wr.wLog("#############################################################################################")
                wr.wLog("Recebida solicitação de contorno em torno de ponto de interesse (e.g. emissor, aeroporto)")

                # mandatory arguments
                latitude = data["latitude"]
                longitude = data["longitude"]
                raio = data["raio"]

                # optional arguments (with defaults)
                numeropontos = data.get("numeropontos", default_points(raio))

                # Present used arguments
                wr.wLog(f"Usuário: {user}, Ponto Inicial: {pontoinicial}")
                wr.wLog(f"Latitude: {latitude}, Longitude: {longitude}, Raio: {raio}m, Número de Pontos: {numeropontos}",level="debug")
                wr.wLog(f"Regiões Evitar: {regioes}",level="debug")
                
                # Process the received data
                central_point = [latitude, longitude]
                fileName,fileNameStatic,fileKml=wr.RouteContorno(   data,
                                                                    user,
                                                                    pontoinicial,
                                                                    central_point,
                                                                    regioes,radius_km=raio,
                                                                    num_points=numeropontos)
                wr.wLog("#############################################################################################")

            case "PontosVisita":
                wr.wLog("#############################################################################################")
                wr.wLog("Recebida solicitação pontos de visita")

                # mandatory arguments
                pontosvisita = data["pontosvisita"]
                
                # Present used arguments
                wr.wLog(f"Usuário: {user}, Ponto Inicial: {pontoinicial}")
                wr.wLog(f"Pontos de Visita: {pontosvisita}",level="debug")
                wr.wLog(f"Regiões Evitar: {regioes}",level="debug")
                
                # Process the received data
                fileName, fileNameStatic, fileKml = wr.RoutePontosVisita(   data,
                                                                            user,
                                                                            pontoinicial,
                                                                            pontosvisita,
                                                                            regioes)
                wr.wLog("#############################################################################################")
            
            case "Abrangencia":
                wr.wLog("#############################################################################################")
                wr.wLog("Recebida solicitação de compromisso de abrangência")

                # mandatory arguments
                cidade = data["cidade"]
                uf = data["uf"]
                escopo = data["Escopo"]
                distanciaPontos = data["distancia_pontos"]
                
                # Present used arguments
                wr.wLog(f"Usuário: {user}, Ponto Inicial: {pontoinicial}")
                wr.wLog(f"Cidade: {cidade},Uf: {uf}, Escopo: {escopo}, Distância entre Pontos: {distanciaPontos} m")
                wr.wLog(f"Regiões Evitar: {regioes}",level="debug")

                # Process the received data
                fileName,fileNameStatic,fileKml=wr.RouteCompAbrangencia(data,
                                                                        user,
                                                                        pontoinicial,
                                                                        cidade,
                                                                        uf,
                                                                        escopo,
                                                                        distanciaPontos,
                                                                        regioes)
                wr.wLog("#############################################################################################")

            case "RoteamentoOSMR":
                wr.wLog("#############################################################################################")
                wr.wLog("Recebida solicitação de RoteamentoOSMR")
                
                # mandatory arguments
                porta = data["PortaOSRMServer"]
                
                # optional arguments
                pontosvisita = data.get("pontosvisita", [])
                pontoinicial = data.get("pontoinicial", [])
                recalcularrota = data.get("recalcularrota",1)
                username =  data["UserName"]
            
                # Processa a requisição
                polylineRota, DistanceTotal, pontosvisita = wr.RoteamentoOSMR(  username,
                                                                                porta,
                                                                                pontosvisita,
                                                                                pontoinicial,
                                                                                recalcularrota)
                cb.cCacheBoundingBox._schedule_save()
                # Retorna uma resposta de confirmação
                wr.wLog(
                    json.dumps(
                        {
                            "polylineRota": polylineRota,
                            "DistanceTotal": DistanceTotal,
                            "RotaRecalculada": recalcularrota,
                            "pontosVisita": pontosvisita,
                        }
                    ),level="debug"
                )
                wr.wLog("#############################################################################################")
                return jsonify(
                    {
                        "polylineRota": polylineRota,
                        "DistanceTotal": DistanceTotal,
                        "RotaRecalculada": recalcularrota,
                        "pontosVisita": pontosvisita,
                    }
                ), 200

            case _:
                return jsonify({"error": f"Tipo de requisição parcialmente definido. Favor atualizar webrota para processamento da requisição `{request_type}`"}), 400
        
        cb.cCacheBoundingBox._schedule_save()
        # Retorna uma resposta de confirmação
        return jsonify(
            {
                "MapaOk": fileName,
                "Url": f"http://127.0.0.1:{env.port}/map/{fileName}",
                "HtmlStatic": f"http://127.0.0.1:{env.port}/download/{fileNameStatic}",
                "Kml": f"http://127.0.0.1:{env.port}/download/{fileKml}",
            }
        ), 200

################################################################################
executor = ThreadPoolExecutor(max_workers=40)
ListaTarefas = []

################################################################################
def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    :return: Parsed arguments.
    """

    parser = argparse.ArgumentParser(description="WebRotas Server")
    parser.add_argument(
        "--port",
        type=int,
        default=env.port,
        help="Porta para o servidor Flask (default: %(default)s)",
    )
    parser.add_argument(
        "--debug",
        type=bool,
        default=env.debug_mode,
        help="Ativa modo de debug (default: %(default)s)",
    )
    
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            wr.wLog(f"Warning: Unknown arguments ignored: {unknown}")
            wr.wLog(f"Using default values: port={env.port}, debug={env.debug_mode}")
        return args
    except Exception as e:
        wr.wLog(f"Error parsing arguments: {e}")
        wr.wLog(f"Using default values: port={env.port}, debug={env.debug_mode}")
        # Return a Namespace with default values
        return argparse.Namespace(port=env.port, debug=env.debug_mode)


################################################################################
def main():
    """Main function to initialize and run the WebRotas server."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Get an available port for the server
        env.get_port(args.port)
        env.save_server_data()
        wr.server_port = env.port

        wr.wLog(f"Starting WebRotas Server on port {env.port}...")
        rsi.init_and_load_podman_images()
        rsi.manutencao_arquivos_antigos()
        gi.cGuiOutput.url = f"http://127.0.0.1:{env.port}/"
        app.run(debug=args.debug, port=env.port, host='0.0.0.0')
        return 0
    except Exception as e:
        wr.wLog(f"Server error: {e}")
        return 1
    finally:
        # Ensure cleanup happens exactly once
        try:
            env.clean_server_data()
            wr.wLog("Exiting WebRotas Server")
        except Exception as e:
            wr.wLog(f"Cleanup error: {e}")


if __name__ == "__main__":
    sys.exit(main())


################################################################################
