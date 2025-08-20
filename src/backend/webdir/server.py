import sys
import requests
import argparse

from flask import (
    Flask,
    Response,
    jsonify,
    send_from_directory,
    request,
    redirect,
)
from flask_cors import CORS
from flask_compress import Compress

import web_rotas
from server_env import env
import routing_servers_interface as rsi
from route_request_manager import RouteRequestManager as rrm

#-----------------------------------------------------------------------------------#
# ESTRUTURA DA REQUISIÇÃO JSON
# - "type"         : "shortest" | "circle" | "grid" | "ordered"
# - "origin"       : objeto com campos "lat" (float), "lng" (float), "description" 
#                    (string) e "elevation" (float, opcional)
# - "parameters"   : objeto com campos dependentes do "type" (ver KEYS_PARAMETERS)
# - "avoidZones" **: lista de objetos, cada um contendo "name"  (string) e "coord" 
#                    (lista de [lat, lng])
# - "criterion"  **: "distance" | "duration" | "ordered"
#
# ** Campos opcionais, cujos valores padrão são [] e "distance", respectivamente.
#-----------------------------------------------------------------------------------#
KEYS_ROOT = {
    "required": { "type", "origin", "parameters" },
    "optional": { "avoidZones", "criterion" } 
}

KEYS_PARAMETERS = {
    "shortest": { "waypoints" },
    "circle":   { "centerPoint", "radius", "totalWaypoints" },    
    "grid":     { "city", "state", "scope", "pointDistance" },
    "ordered":  { "routeId", "cacheId", "boundingBox", "waypoints" }
}

#-----------------------------------------------------------------------------------#
# SERVIDOR
# Utilizado "FLASK" nesta versão; em produção deverá ser migrado para outro framework
# (FastAPI, NodeJS etc).
# - "/" ou "/webRotas" :
#       Redireciona para "/webRotas/index.html", servindo arquivo estático.
# - "/<path:filepath>" :
#       Serve arquivos estáticos a partir da pasta "static".
# - "/process" :
#       Processa requisições HTTP onde:
#           • A URL deve conter o parâmetro "sessionId".
#           • O body deve conter campos listados em KEYS_ROOT e KEYS_PARAMETERS.
# - "/ok" :
#       Endpoint de verificação ("ping") entre servidor e clientes.
#-----------------------------------------------------------------------------------#
app = Flask(__name__, static_folder="static", static_url_path="/webRotas")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = False
CORS(app)
Compress(app)

#-----------------------------------------------------------------------------------#
@app.route("/", methods=["GET"])
@app.route("/webRotas", methods=["GET"])
def _root():
    return redirect("/webRotas/index.html")

#-----------------------------------------------------------------------------------#
@app.route("/<path:filepath>", methods=["GET"])
def _static_files(filepath):
    return send_from_directory("static", filepath)

#-----------------------------------------------------------------------------------#
@app.route("/process", methods=["POST"])
def _process():
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "Invalid or missing sessionId"}), 400

    data = request.get_json()
    if not data or not KEYS_ROOT['required'].issubset(data.keys()):
        return jsonify({"error": f"Invalid or missing JSON payload. Required fields: {list(KEYS_ROOT['required'])}"}), 400

    request_type = data.get("type")
    if not request_type or request_type not in KEYS_PARAMETERS:
        return jsonify({"error": "Invalid or missing request type"}), 400

    parameters = data.get("parameters")
    if not isinstance(parameters, dict):
        return jsonify({"error": "Parameters field must be a JSON object"}), 400

    missing_params = KEYS_PARAMETERS[request_type] - parameters.keys()
    if missing_params:
        return jsonify({"error": f"Missing required parameters for type '{request_type}': {list(missing_params)}"}), 400

    return controller(data, session_id)

#-----------------------------------------------------------------------------------#
@app.route("/ok", methods=["GET"])
def _ok():
    session_id = request.args.get("sessionId")
    if not session_id:
        return jsonify({"error": "Invalid or missing sessionId"}), 400
    
    return "ok"

#-----------------------------------------------------------------------------------#
def controller(data: dict, session_id: str):
    try:
        request_type = data["type"]
        origin       = data["origin"]        
        parameters   = data["parameters"]
        avoid_zones  = data.get("avoidZones", [])
        criterion    = data.get("criterion", "distance")

        current_request, new_request_flag = rrm.process_request(request_type, data)
        status = "[webRotas] Created new request" if new_request_flag else "Using existing request"
        print(f'{status} routeId="{current_request.route_id}" (type="{request_type}", criterion="{criterion}", sessionId="{session_id}")')
    
        match request_type:
            case "shortest":
                web_rotas.osrm_shortest(
                    current_request,
                    session_id,
                    origin,
                    parameters["waypoints"],
                    avoid_zones,
                    criterion
                )
            case "circle":
                web_rotas.osrm_circle(
                    current_request,
                    session_id,
                    origin,
                    parameters["centerPoint"],
                    parameters["radius"],
                    parameters["totalWaypoints"],
                    avoid_zones,
                    criterion
                )
            case "grid":
                web_rotas.osrm_grid(
                    current_request,
                    session_id,
                    origin,
                    parameters["city"],
                    parameters["state"],
                    parameters["scope"],
                    parameters["pointDistance"],
                    avoid_zones,
                    criterion
                )
            case "ordered":
                web_rotas.osrm_ordered(
                    current_request,
                    session_id,
                    origin,
                    parameters["cacheId"],
                    parameters["boundingBox"],
                    parameters["waypoints"],
                    avoid_zones,
                    criterion
                )

        if request_type in { "shortest", "circle", "grid" }:
            response = current_request.create_initial_route()
        else:
            response = current_request.create_custom_route()

        return Response(response, mimetype="application/json")

    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500

#-----------------------------------------------------------------------------------#
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
            print(f"[webRotas] Warning: Unknown arguments ignored: {unknown}")
            print(f"[webRotas] Using default values: port={env.port}, debug={env.debug_mode}")
        return args
    
    except Exception as e:
        print(f"[webRotas] Error parsing arguments: {e}")
        print(f"[webRotas] Using default values: port={env.port}, debug={env.debug_mode}")
        # Return a Namespace with default values
        return argparse.Namespace(port=env.port, debug=env.debug_mode)

#-----------------------------------------------------------------------------------#
def main():
    try:
        args = parse_args()

        ## Server Port ##
        env.get_port(args.port)
        env.save_server_data()

        """
        ## Podman check ##
        rsi.init_and_load_podman_images()
        status, message = rsi.is_podman_running_health()
        if status:
            print("[webRotas] Podman is healthy and operational.")
        else:
            print(f"[webRotas] Podman is not healthy {message}")  
        
        rsi.manutencao_arquivos_antigos()
        """

        ## Flask app ##
        app.run(debug=False, port=env.port, host="0.0.0.0")
        return 0
    
    except Exception as e:
        print(f"[webRotas] Server error: {e}")
        return 1
    
    finally:
        try:
            env.clean_server_data()
            print("[webRotas] Exiting server")
        except Exception as e:
            print(f"[webRotas] Cleanup error: {e}")

#-----------------------------------------------------------------------------------#
# DEBUG
#-----------------------------------------------------------------------------------#
if __name__ == "__main__":
    sys.exit(main())