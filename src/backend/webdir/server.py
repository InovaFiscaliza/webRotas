#!/usr/bin/env python3
"""
Provê servidor web para cálculo de rotas.

:args:
    --port: Porta para o servidor Flask (default: 5001)
    --debug: Ativa modo de debug (default: False)
"""

import sys
import requests
import argparse
from unidecode import unidecode

from flask import (
    Flask,
    Response,
    jsonify,
    send_from_directory,
    request,
    redirect,
)
from flask_compress import Compress
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

import wlog as wl
import webRota as wr

from server_env import env
import routing_servers_interface as rsi
import CacheBoundingBox as cb
from route_request_manager import RouteRequestManager as rrm


# -----------------------------------------------------------------------------------#
# VARIÁVEIS GLOBAIS
# -----------------------------------------------------------------------------------#
REQUIRED_KEYS_ROOT = { 
    "type", 
    "origin", 
    "avoidZones", 
    "parameters" 
}

REQUIRED_KEYS_PARAMETERS = {
    "shortest": { "waypoints" },
    "circle":   { "centerPoint", "radius", "totalWaypoints" },    
    "grid":     { "city", "state", "scope", "pointDistance" },
    "ordered":  { "routeId", "cacheId", "boundingBox", "waypoints", "neededPaths" }
}

executor = ThreadPoolExecutor(max_workers=40)
ListaTarefas = []

wl.set_log_filename(env.log_file)
wl.wLog(f"Arquivo de log: {env.log_file}")


# -----------------------------------------------------------------------------------#
# FLASK
# -----------------------------------------------------------------------------------#
app = Flask(__name__, static_folder="static", static_url_path="/webRotas")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = False
CORS(app)
Compress(app)

# -----------------------------------------------------------------------------------#
@app.route("/", methods=["GET"])
@app.route("/webRotas", methods=["GET"])
def _root():
    return redirect("/webRotas/index.html")

# -----------------------------------------------------------------------------------#
@app.route("/<path:filepath>", methods=["GET"])
def _static_files(filepath):
    return send_from_directory("static", filepath)

# -----------------------------------------------------------------------------------#
@app.route("/process", methods=["POST"])
def _process():
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "Invalid or missing sessionId"}), 400

    data = request.get_json()
    if not data or not REQUIRED_KEYS_ROOT.issubset(data.keys()):
        return jsonify({"error": f"Invalid or missing JSON payload. Required fields: {list(REQUIRED_KEYS_ROOT)}"}), 400

    request_type = data.get("type")
    if not request_type or request_type not in REQUIRED_KEYS_PARAMETERS:
        return jsonify({"error": "Invalid or missing request type"}), 400

    parameters = data.get("parameters")
    if not isinstance(parameters, dict):
        return jsonify({"error": "Parameters field must be a JSON object"}), 400

    missing_params = REQUIRED_KEYS_PARAMETERS[request_type] - parameters.keys()
    if missing_params:
        return jsonify({"error": f"Missing required parameters for type '{request_type}': {list(missing_params)}"}), 400

    controller(data, session_id)

# -----------------------------------------------------------------------------------#
@app.route("/ok", methods=["GET"])
def _ok():
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "Invalid or missing sessionId"}), 400
    
    return "ok"

# -----------------------------------------------------------------------------------#
@app.route("/route", methods=["GET"])
def get_route():
    """
    Rota Flask que envia requisições para o servidor OSRM e retorna a resposta.
       curl "http://127.0.0.1:5001/route?porta=5001&start=-46.6388,-23.5489&end=-46.6253,-23.5339"
    """
    # Parâmetros da requisição (origem e destino)
    start = request.args.get("start")  # Formato esperado: "lon,lat"
    end   = request.args.get("end")    # Formato esperado: "lon,lat"

    porta = request.args.get("porta")
    OSRM_SERVER_URL = f"http://127.0.0.1:{porta}"

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
        coords_list = [start, end]
        return jsonify(coords_list), 200

# -----------------------------------------------------------------------------------#
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
        return (
            jsonify({"error": f"Falha na comunicação com o servidor OSRM: {str(e)}"}),
            500,
        )


# -----------------------------------------------------------------------------------#
# FUNÇÕES
# -----------------------------------------------------------------------------------#
def controller(data: dict, session_id: str):
    with app.app_context():
        # rsi.keep_last_n_containers_running()
        
        request_type = data["type"]
        origin       = data["origin"]
        avoid_zones  = data["avoidZones"]
        parameters   = data["parameters"]

        current_request, new_request_flag = rrm.process_request(request_type, data)
        status = "Created new request" if new_request_flag else "Using existing request"
        wr.wLog(f'{status} routeId="{current_request.route_id}" (type="{request_type}", sessionId="{session_id}")')

        try:
            match request_type:
                case "shortest":
                    wr.osrm_shortest(
                        current_request,
                        session_id,
                        origin,
                        avoid_zones,
                        parameters["waypoints"]
                    )
                case "circle":
                    wr.osrm_circle(
                        current_request,
                        session_id,
                        origin,
                        avoid_zones,
                        parameters["centerPoint"],
                        parameters["radius"],
                        parameters["totalWaypoints"]
                    )
                case "grid":
                    wr.osrm_grid(
                        current_request,
                        session_id,
                        origin,
                        avoid_zones,
                        parameters["city"],
                        parameters["state"],
                        parameters["scope"],
                        parameters["pointDistance"]
                    )
                case "ordered":
                    wr.osrm_ordered(
                        current_request,
                        session_id,
                        parameters["cacheId"],
                        parameters["boundingBox"],
                        parameters["waypoints"],
                        parameters["neededPaths"]
                    )

            if request_type in {"shortest", "circle", "grid"}:
                response = current_request.create_initial_route()
            else:
                response = current_request.create_custom_route()

            #cb.cCacheBoundingBox._schedule_save()
            return Response(response, mimetype="application/json")

        except Exception as e:
            return jsonify({"error": f"{str(e)}"}), 500


# -----------------------------------------------------------------------------------#
# MIGRAR PARA WEBROTA.OSRM_CIRCLE
# -----------------------------------------------------------------------------------#
def default_points(radi: int) -> int:
    """Calcula o número de pontos padrão para a rota de contorno à partir do raio
    :param radi: Raio em metros
    :return: Número de pontos padrão
    """
    MIN_POINTS = 9
    POINTS_PER_KM = 2
    TWO_PI = 6.28318530718

    return max(MIN_POINTS, int(TWO_PI * radi * POINTS_PER_KM / 1000))

# -----------------------------------------------------------------------------------#
def parse_args() -> argparse.Namespace:
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

# -----------------------------------------------------------------------------------#
def main():
    try:
        args = parse_args()

        ## Server Port ##
        env.get_port(args.port)
        env.save_server_data()
        wr.server_port = env.port

        ## Podman check ##
        rsi.init_and_load_podman_images()
        status, message = rsi.is_podman_running_health()
        if status:
            wr.wLog("Podman is healthy and operational.")
        else:
            wr.wLog(f"Podman is not healthy {message}")  
        
        rsi.manutencao_arquivos_antigos()

        ## Flask app ##
        wr.wLog(f"Starting webRotas server on port {env.port}...")
        app.run(debug=args.debug, port=env.port, host="0.0.0.0")
        return 0
    
    except Exception as e:
        wr.wLog(f"Server error: {e}")
        return 1
    
    finally:
        try:
            env.clean_server_data()
            wr.wLog("Exiting webRotas Server")
        except Exception as e:
            wr.wLog(f"Cleanup error: {e}")

# -----------------------------------------------------------------------------------#
if __name__ == "__main__":
    sys.exit(main())