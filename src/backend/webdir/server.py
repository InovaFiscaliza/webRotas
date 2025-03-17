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

from flask import (
    Flask,
    render_template,
    jsonify,
    send_file,
    request,
) 
from flask_compress import Compress
from flask_cors import CORS

from concurrent.futures import ThreadPoolExecutor

import webRota as wr
import server_env as se

################################################################################
""" Variáveis globais """

env = se.ServerEnv()

################################################################################
# TODO #4 Use standard paths defined in a configuration section or file. May use ProgramData/Anatel/WebRotas, as other applications from E!, where ProgramData folder should use system variables.

wr.log_filename = env.log_file
print(f"Arquivo de log: {env.log_file}")

app = Flask(__name__, static_folder="static")
CORS(app)  # Habilita CORS para todas as rotas
Compress(app)
# Configuração para forçar a recarga de arquivos estáticos
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True  # Ativa o auto-reload dos templates

################################################################################
@app.route("/ok", methods=["GET"])
def ok():
    return "ok"


################################################################################
@app.route("/map/<filename>")
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
@app.route("/route", methods=["GET"])
def get_route():
    """
    Rota Flask que envia requisições para o servidor OSRM e retorna a resposta.\n
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


################################################################################
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


################################################################################
def SalvaDataArq(data):
    # Salva os dados em um arquivo com o nome do usuário
    user = data["User"]
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
    if TipoReq=="Contorno":    # if TipoReq=="DriveTest":
       # Obtém valores do JSON
           # Verifica se todos os campos necessários estão presentes

       print("\n\n#############################################################################################")
       print("Recebida solicitação de contorno em torno de ponto ou aeroporto\n")
       if not all(key in data for key in ("latitude", "longitude", "raio")):
          return jsonify({"error": "Campos latitude, longitude e raio são necessários"}), 400

            user = data["User"]

            latitude = data["latitude"]
            longitude = data["longitude"]
            raio = data["raio"]
            regioes = data.get("regioes", [])
            numeropontos = data["numeropontos"]
            pontoinicial = data.get("PontoInicial", [])

       # Processa os dados (exemplo: exibe no console)
       print(f"Latitude: {latitude}, Longitude: {longitude}, Raio: {raio}")
       central_point = [latitude, longitude]
       fileName,fileNameStatic,fileKml=wr.RouteContorno(data,user,pontoinicial,central_point,regioes,radius_km=raio,num_points=numeropontos)
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

            user = data["User"]
            pontosvisita = data.get("pontosvisita", [])
            regioes = data.get("regioes", [])
            pontoinicial = data.get("PontoInicial", [])
            # Processa os dados (exemplo: exibe no console)
            print(f"pontosvisita: {pontosvisita},  Regiões Evitar: {regioes}")
            fileName, fileNameStatic, fileKml = wr.RoutePontosVisita(
                data, user, pontoinicial, pontosvisita, regioes
            )
            # Retorna uma resposta de confirmação
            return jsonify(
                {
                    "MapaOk": fileName,
                    "Url": f"http://127.0.0.1:{env.port}/map/{fileName}",
                    "HtmlStatic": f"http://127.0.0.1:{env.port}/download/{fileNameStatic}",
                    "Kml": f"http://127.0.0.1:{env.port}/download/{fileKml}",
                }
            ), 200
        # ---------------------------------------------------------------------------------------------
        TipoReq = data["TipoRequisicao"]
        if TipoReq == "Abrangencia":
            # Obtém valores do JSON
            print(
                "\n\n#############################################################################################"
            )
            print("Recebida solicitação de compromisso de abrangência\n")
            # https://informacoes.anatel.gov.br/legislacao/procedimentos-de-fiscalizacao/1724-portaria-2453
            if not all(
                key in data for key in ("cidade", "distancia_pontos", "regioes")
            ):
                return jsonify(
                    {
                        "error": "Campos cidade, distancia_pontos e regioes são necessários"
                    }
                ), 400

       user=data["User"]
       pontoinicial = data.get("PontoInicial", [])
       cidade = data["cidade"]
       uf = data["uf"]
       escopo = data["Escopo"]
       distanciaPontos = data["distancia_pontos"]
       regioes = data["regioes"]

       # Processa os dados (exemplo: exibe no console)
       print(f"Cidade: {cidade},Uf: {uf}, distancia_pontos: {distanciaPontos} m, Regiões Evitar: {regioes}")
       fileName,fileNameStatic,fileKml=wr.RouteCompAbrangencia(data,user,pontoinicial,cidade,uf,escopo,distanciaPontos,regioes)
       # Retorna uma resposta de confirmação
       return jsonify({"MapaOk": fileName,"Url":f"http://127.0.0.1:5001/map/{fileName}",
                       "HtmlStatic":f"http://127.0.0.1:5001/download/{fileNameStatic}",
                       "Kml":f"http://127.0.0.1:5001/download/{fileKml}"}
                      ), 200
    #---------------------------------------------------------------------------------------------
    TipoReq = data["TipoRequisicao"]
    if TipoReq=="RoteamentoOSMR":
       # Obtém valores do JSON
       wr.wLog("\n\n#############################################################################################")
       wr.wLog("Recebida solicitação de RoteamentoOSMR\n")

            if not all(
                key in data
                for key in ("TipoRequisicao", "PortaOSRMServer", "pontosvisita")
            ):
                return jsonify(
                    {
                        "error": "Campos TipoRequisicao, PortaOSRMServer e pontosvisita são necessários"
                    }
                ), 400

            porta = data["PortaOSRMServer"]
            pontosvisita = data.get("pontosvisita", [])
            pontoinicial = data.get("pontoinicial", [])
            recalcularrota = data.get("recalcularrota")
            polylineRota, DistanceTotal, pontosvisita = wr.RoteamentoOSMR(
                porta, pontosvisita, pontoinicial, recalcularrota
            )
            # Retorna uma resposta de confirmação
            wr.wLog(
                json.dumps(
                    {
                        "polylineRota": polylineRota,
                        "DistanceTotal": DistanceTotal,
                        "RotaRecalculada": recalcularrota,
                        "pontosVisita": pontosvisita,
                    }
                )
            )
            wr.wLog(
                "\n\n#############################################################################################"
            )
            return jsonify(
                {
                    "polylineRota": polylineRota,
                    "DistanceTotal": DistanceTotal,
                    "RotaRecalculada": recalcularrota,
                    "pontosVisita": pontosvisita,
                }
            ), 200

        # ---------------------------------------------------------------------------------------------
        return jsonify({"ErroPedido": "ErroPedido"}), 200


################################################################################
executor = ThreadPoolExecutor(max_workers=40)
ListaTarefas = []


################################################################################
@app.route("/download/<filename>")
def download_file(filename):
    # Caminho absoluto ou relativo para o arquivo
    caminho_arquivo = f"templates/{filename}"
    try:
        return send_file(caminho_arquivo, as_attachment=True)
    except Exception as e:
        return f"Erro ao enviar o arquivo: {e}"


################################################################################
@app.route("/webrotas", methods=["POST"])
def process_location():
    # Obtém o JSON da requisição
    data = request.get_json()
    return ProcessaRequisicoesAoServidor(data)


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
            print(f"Warning: Unknown arguments ignored: {unknown}")
            print(f"Using default values: port={env.port}, debug={env.debug_mode}")
        return args
    except Exception as e:
        print(f"Error parsing arguments: {e}")
        print(f"Using default values: port={env.port}, debug={env.debug_mode}")
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

        print(f"\nStarting WebRotas Server on port {env.port}...")
        app.run(debug=args.debug, port=env.port, host='0.0.0.0')
        return 0
    except Exception as e:
        print(f"Server error: {e}")
        return 1
    finally:
        # Ensure cleanup happens exactly once
        try:
            env.clean_server_data()
            print("\nExiting WebRotas Server\n")
        except Exception as e:
            print(f"Cleanup error: {e}")


if __name__ == "__main__":
    sys.exit(main())


################################################################################
