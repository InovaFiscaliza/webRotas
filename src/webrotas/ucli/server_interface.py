#!/usr/bin/env python3
"""
Interact with the WebRotas server.
"""

import os
import logging
import json
import requests
import subprocess
import time
import webbrowser
from pathlib import Path
from webrotas.config.server_hosts import get_webrotas_host


SERVER_NAME = "WebRotas Server"
SERVER_PORT = 5001
SERVER_ROOT_URL = None  # Set dynamically in update_url_port()
SERVER_TEST_URL_FOLDER = "/ok"
SERVER_URL_FOLDER = "/webrotas"
PROJECT_FOLDER_NAME = "webRotas"
SERVER_DATA_FILE = "src//TempData/server.json"
SERVER_PROJECT_RELATIVE_PATH = "src//server.py"
SERVER_START_TIMEOUT = 10  # Tempo de espera para o servidor iniciar em segundos
SERVER_WAIT_TIMEOUT = 60  # Tempo para desistir de esperar o servidor em segundos
URL_RESPONSE_TIMEOUT = 5  # Tempo de espera para resposta do servidor em segundos
VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 404]
DETACHED_PROCESS = 0x00000008


# ----------------------------------------------------------------------------------------------
class ServerError(Exception):
    pass


# ----------------------------------------------------------------------------------------------
class ServerData:
    def __init__(self):
        self.name: str = SERVER_NAME
        """ Server name. """
        self.status_up: bool = False
        """ Server status. True if server is running, False otherwise."""
        self.port: int = SERVER_PORT
        """ Server port number. """
        self.test_url: str
        """ URL to test if the server is running. """
        self.url: str
        """ URL to send the JSON payload. """
        self.base_path: str = os.path.realpath(__file__)
        """ Path to the script file. """
        self.server_project_path: str = self.build_project_path()
        """ Path to the project folder. """
        self.server_data_file: str = self.build_server_data_filename()
        """ Path to the server data file. """

        self.load_server_data()
        self.update_url_port()

    # ------------------------------------------------------------------------------------------
    def build_project_path(self) -> str:
        """
        Make the project path from the script path and the project name.

        :return: Path to the project folder.
        """
        return os.path.normpath(
            self.base_path[
                : self.base_path.rfind(PROJECT_FOLDER_NAME) + len(PROJECT_FOLDER_NAME)
            ]
        )

    # ------------------------------------------------------------------------------------------
    def build_server_data_filename(self) -> str:
        """
        Make the server data file path from the project path.

        :return: Path to the server data file.
        """
        return os.path.normpath(
            os.path.join(self.server_project_path, SERVER_DATA_FILE)
        )

    # ------------------------------------------------------------------------------------------
    def update_url_port(self) -> None:
        """
        Update URL values using the server port number.
        """
        host = get_webrotas_host()
        base_url = f"http://{host}:"
        self.test_url = f"{base_url}{self.port}{SERVER_TEST_URL_FOLDER}"
        self.url = f"{base_url}{self.port}{SERVER_URL_FOLDER}"

    # ------------------------------------------------------------------------------------------
    def load_server_data(self):
        """
        Load server data from the server data file.
        """
        try:
            with open(self.server_data_file, "r") as f:
                server_data = json.load(f)
                self.port = server_data.get("port", SERVER_PORT)
                self.status_up = True
        except FileNotFoundError:
            logging.info(
                f"File {self.server_data_file} not found. Server will be started"
            )
            self.status_up = False
        except json.JSONDecodeError:
            logging.error(f"Error decoding data from file {self.server_data_file}.")
            self.status_up = False
        except Exception as e:
            logging.error(f"Unidentified error loading {self.server_data_file}: {e}")
            self.status_up = False

    # ----------------------------------------------------------------------------------------------
    def is_http_ok(self) -> bool:
        """
        Test if server http service is running.

        :return: True if server is running, False otherwise.
        """
        try:
            response = requests.get(self.test_url, timeout=URL_RESPONSE_TIMEOUT)
            return response.status_code in VALID_STATUS_CODES
        except requests.RequestException:
            return False

    # ----------------------------------------------------------------------------------------------
    def is_running(self) -> bool:
        """
        Check if the server is running. If not, try to start it.

        :return: True if the server is running, False otherwise.
        """

        # If server data file is missing, server.status_up is False and just move to start the server passing 2 ifs.
        # Else test the access to server page before continuing.
        if self.status_up:
            self.status_up = self.is_http_ok()

        # If server page is up, return True.
        if self.status_up:
            logging.info("Routing service is running.")
        else:
            # command = (
            #    f"title {self.name} && "
            #    f"cd {self.server_project_path} && "
            #    f"uv run .\\src\\backend\\webdir\\server.py --port {self.port}"
            # )
            # print(f"cd {self.server_project_path} && ")
            # print(f"uv run .\\src\\backend\\webdir\\server.py --port {self.port}")
            # subprocess.Popen(command, creationflags=DETACHED_PROCESS, shell=True)

            server_abs_path = (
                Path(self.server_project_path) / SERVER_PROJECT_RELATIVE_PATH
            )
            command = f"uv run --project {self.server_project_path} {server_abs_path} --port {self.port}"
            subprocess.Popen(command, creationflags=DETACHED_PROCESS, shell=True)

            countdown = SERVER_WAIT_TIMEOUT / SERVER_START_TIMEOUT
            while not self.status_up:
                time.sleep(SERVER_START_TIMEOUT)
                countdown -= 1

                self.load_server_data()
                self.status_up = self.is_http_ok()

                if countdown <= 0:
                    logging.info("Timeout. Could not start routing service.")
                    return False

                if not self.status_up:
                    logging.info("Waiting for routing service to start.")
                else:
                    logging.info("Routing service started.")

        return True

    # ----------------------------------------------------------------------------------------------
    def send_payload(self, payload: dict) -> None:
        """
        Send a JSON payload to the WebRotas server.

        :param payload: JSON payload to send.
        :param url: URL to send the payload.
        """

        try:
            response = requests.post(self.url, json=payload)

            if response.status_code == 200:
                response_dict = response.json()
                logging.info(
                    "\n-----------------------------------------------\n"
                    f" Interactive page: {response_dict['Url']}\n"
                    f" Download kml: {response_dict['Kml']}\n"
                    f" Download http: {response_dict['HtmlStatic']}\n"
                    "-----------------------------------------------"
                )
                webbrowser.open(response_dict["Url"])
            else:
                raise ServerError(
                    f"Server returned {response.status_code}: {response.text}"
                )
        except requests.RequestException as e:
            raise ServerError(f"Request error: {e}") from e
