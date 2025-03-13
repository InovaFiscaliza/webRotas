#!/usr/bin/env python3
"""
Send a JSON payload to the WebRotas server.
"""

import requests
import webbrowser
import subprocess
import sys
import os
import time
import logging
import json
import argparse


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEMO_PAYLOAD = {
    "User": "Alessandro",
    "TipoRequisicao": "PontosVisita",
    "PontoInicial": [
        2.802119889276001,
        -60.68869135518992,
        "Anatel Roraima",
    ],  
    "RaioDaEstacao": 200,
    "GpsProximoPonto": "ProximoDaRota",  
    "pontosvisita": [
        [2.812482, -60.670263, "Local", "Parque do Rio Branco"],
        [2.840826, -60.692496, "Local", "Aeroporto Internacional de Boa Vista"],
        [2.854428, -60.644444, "Local", "Roraima Garden Shopping"],
        [2.831661, -60.662501, "Local", "Estádio Flamarion Vasconcelos"],
        [2.827492, -60.680001, "Local", "Praça Fábio Paracat"],
        [2.791658, -60.694723, "Local", "Área Militar – 7º BIS"],
        [2.850549, -60.706111, "Local", "Pátio Roraima Shopping"],
        [2.807220, -60.738611, "Local", "Praça e Palco Aderval da Rocha Ferreira"],
        [2.892775, -60.705277, "Local", "Bairro Pedra Pintada, p/ super. Salmos 23"],
        [2.764720, -60.713611, "Local", "Distrito Industrial de Boa Vista - Roraima"],
        [2.837220, -60.684445, "Local", "Parque Anauá"],
        [2.844719, -60.754723, "Local", "Bairro Cidade Satélite"],
        [2.817774, -60.728333, "Local", "Rua São Sebastião com Ataide Teive"],
        [2.814996, -60.696664, "Local", "Hospital do Amor - Bairro Pericumã"],
        [2.769164, -60.731389, "Local", "Bairro Nova Cidade – Escola Est. Dr. Luiz"],
        [2.838887, -60.718613, "Local", "Fórum Criminal – Bairro Caranã"],
        [2.811386, -60.711945, "Local", "Senai – RR, Bairro Asa Branca"],
        [2.803887, -60.691666, "Local", "Hosp. Materno Infantil Bairro 13 de Set."],
        [2.793886, -60.715556, "Local", "CRAS/Cristiana Vicente Nunes"],
        [2.816383, -60.772500, "Local", "Praça Cruviana – Bairro Jardin Equatorial"],
    ],
    "AlgoritmoOrdenacaoPontos": "DistanciaGeodesica",
    "regioes": [
                {       
                    "nome": "Nova Vida",
                    "coord": [
                        [2.790102332336339,-60.710362124135997],
                        [2.787367590960403,-60.710993735166312],
                        [2.781447917367775,-60.703978821170054],
                        [2.783551047713397,-60.702070549546548],
                        [2.785822159716017,-60.703703331252576],
                        [2.787313836830164,-60.70534955149116],
                        [2.78887942587339,-60.707795364417059],
                        [2.78887942587339,-60.707795364417059],
                        [2.78887942587339,-60.707795364417059],
                        [2.790102332336339,-60.710362124135997]
                    ]
                },
                {
                    "nome": "Ocupação no Bairro Aracelis",
                    "coord": [
                        [2.794846134329978,-60.724674161312223],
                        [2.791271484669049,-60.725520788863491],
                        [2.789779807554902,-60.72135484376993],
                        [2.793233510422792,-60.720360392360497],
                        [2.794819257264858,-60.721287651107133],
                        [2.795249290306774,-60.722980906209678],
                        [2.794846134329978,-60.724674161312223]
                    ] 
                }
    ],
}

SERVER_NAME = "WebRotas Server"
SERVER_PORT = 5001
SERVER_ROOT_URL = "http://localhost:"
SERVER_TEST_URL_FOLDER = "/ok"
SERVER_URL_FOLDER = "/webrotas"
PROJECT_FOLDER_NAME = "webRotas"
SERVER_DATA_FILE = "src/backend/webdir/TempData/server.json"
SERVER_START_TIMEOUT = 10 # Tempo de espera para o servidor iniciar em segundos
SERVER_WAIT_TIMEOUT = 60 # Tempo para desistir de esperar o servidor em segundos
URL_RESPONSE_TIMEOUT = 5 # Tempo de espera para resposta do servidor em segundos
VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 404]

DETACHED_PROCESS = 0x00000008

# ----------------------------------------------------------------------------------------------
class ServerData:
    def __init__(self):
        self.name: str = SERVER_NAME
        """ Server name. """
        self.status_up: bool = False
        """ Server status. True if server is running, False otherwise."""
        self.port: int = SERVER_PORT
        """ Server port number. """
        self.test_url: str = f"{SERVER_ROOT_URL}{self.port}{SERVER_TEST_URL_FOLDER}"
        """ URL to test if the server is running. """	
        self.url: str = f"{SERVER_ROOT_URL}{self.port}{SERVER_URL_FOLDER}"
        """ URL to send the JSON payload. """
        self.base_path: str = os.path.realpath(__file__)
        """ Path to the script file. """
        self.server_project_path: str = self.build_project_path()
        """ Path to the project folder. """
        self.server_data_file: str = self.build_server_data_filename()
        """ Path to the server data file. """
        
        self.load_server_data()

    # ------------------------------------------------------------------------------------------
    def build_project_path(self) -> str:
        """
        Make the project path from the script path and the project name.
        
        :return: Path to the project folder.
        """
        return self.base_path[:self.base_path.find(PROJECT_FOLDER_NAME) + len(PROJECT_FOLDER_NAME)]
    
    def build_server_data_filename(self) -> str:
        """
        Make the server data file path from the project path.
        
        :return: Path to the server data file.
        """
        return os.path.join(os.path.dirname(self.server_project_path), SERVER_DATA_FILE)
    
    # ------------------------------------------------------------------------------------------
    def load_server_data(self):
        """
        Load server data from the server data file.
        """
        try:
            with open(self.server_data_file, "r") as f:
                server_data = json.load(f)
                self.port = server_data.get("port", SERVER_PORT)
                self.test_url = f"{SERVER_ROOT_URL}{self.port}{SERVER_TEST_URL_FOLDER}"
                self.url = f"{SERVER_ROOT_URL}{self.port}{SERVER_URL_FOLDER}"
                self.status_up = True
        except FileNotFoundError:
            logging.error(f"File {self.server_data_file} not found.")
            self.status_up = False
        except json.JSONDecodeError:
            logging.error(f"Error decoding data from file {self.server_data_file}.")
            self.status_up = False
        except Exception as e:
            logging.error(f"Unidentified error loading {self.server_data_file}: {e}")
            self.status_up = False

# ----------------------------------------------------------------------------------------------
def is_server_running(url: str) -> bool:
    """
    Test if server is running.

    :param url: Server URL to test.
    :return: True if server is running, False otherwise.
    """
    try:
        response = requests.get(url, timeout=URL_RESPONSE_TIMEOUT)
        return response.status_code in VALID_STATUS_CODES
    except requests.RequestException:
        return False

# ----------------------------------------------------------------------------------------------
def server_is_fine(server: ServerData) -> bool:
    """
    Check if the server is running. If not, try to start it.
    
    :param test_url: URL to test if the server is running.
    :return: True if the server is running, False otherwise.
    """
    
    # Initial value of server.status_up reflects the presence of server.json status file.
    # Actual server test must be performed before continuing.
    if server.status_up:
        server.status_up = is_server_running(url=server.test_url)
    
    if server.status_up:
        logging.info("Server is ok.")
    else:
        command = f"title {server.name} && cd {server.server_project_path} && uv run .\\src\\backend\\webdir\\server.py --port {server.port}"

        subprocess.Popen(command, creationflags=DETACHED_PROCESS, shell=True)
    
        countdown = SERVER_WAIT_TIMEOUT / SERVER_START_TIMEOUT
        while not server.status_up:
            time.sleep(SERVER_START_TIMEOUT)
            countdown -= 1
            
            server.load_server_data()
            server.status_up = is_server_running(url=server.test_url)
            
            if countdown <= 0:
                logging.info("Timeout. Server not started.")
                return False
            
            if not server.status_up:
                logging.info("Waiting for server to start.")
            else:
                logging.info("Server started.")
            
    return True

# ----------------------------------------------------------------------------------------------
def send_json(payload: dict, url: str) -> None:
    """
    Send a JSON payload to the WebRotas server.

    :param payload: JSON payload to send.
    :param url: URL to send the payload.
    """

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            response_dict = response.json()
            logging.info(   "-----------------------------------------------\n",
                            f" Interactive page: {response_dict['Url']}\n",
                            f" Download kml: {response_dict['Kml']}\n",
                            f" Download http: {response_dict['HtmlStatic']}\n",
                            "-----------------------------------------------")
            webbrowser.open(response_dict['Url'])
        else:
            logging.error("Error {response.status_code}: {response.text}")
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")


# ----------------------------------------------------------------------------------------------
def main() -> int:

    parser = argparse.ArgumentParser(description="Send a JSON payload to the WebRotas server.")
    parser.add_argument("payload", nargs="?", default=None, help="Name of the JSON file containing the payload to be sent.")
    args = parser.parse_args()

    if args.payload is None:
        logging.warning("Using default payload as example.")
        parser.print_help()
        payload = DEMO_PAYLOAD
    else:
        try:
            with open(args.payload, "r") as f:
                payload = json.load(f)
        except FileNotFoundError:
            logging.error(f"\nFile {args.payload} not found.\n")
            parser.print_help()
            return 1    
    
    server = ServerData()
    
    if server_is_fine(server=server):
        send_json(payload=payload, url=server.url)


if __name__ == "__main__":
    sys.exit(main())
