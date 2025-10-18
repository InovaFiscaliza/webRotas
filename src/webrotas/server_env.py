"""
Define and manage the server environment
"""

import os
import json
import webrotas.port_test as pt

# ---------------------------------------------------------------------------
"""	Constants	"""

PREFERRED_PORT = 5002
DEBUG_MODE = False
LOG_FILE_PATH = "logs/webRotas"
SERVER_DATA_PATH = "config/server.json"


# ---------------------------------------------------------------------------
class ServerEnv:
    def __init__(self):
        self.port: int = PREFERRED_PORT

        """Port number for the server."""
        self.debug_mode: bool = DEBUG_MODE

        """Debug mode for the server."""
        self.script_path: str = os.path.realpath(__file__)

        """Path to the script file."""
        self.server_data_file: str = SERVER_DATA_PATH

        """Path to the server data file."""
        self.log_file: str = LOG_FILE_PATH

        """Path to the log file."""
        self.required_paths: list = []

        """List of required folders for the server."""
        self.set_paths()
        self.test_required_paths()

    # ---------------------------------------------------------------------------
    def set_paths(self) -> None:
        """Change the current working directory to the directory of the script.\n
        Avoid error if script is called from a folder different from the script's folder.
        """
        cd = os.path.dirname(self.script_path)
        os.chdir(cd)

        self.server_data_file = os.path.normpath(os.path.join(cd, SERVER_DATA_PATH))
        self.log_file = os.path.normpath(os.path.join(cd, LOG_FILE_PATH))
        self.required_paths = [
            os.path.dirname(self.server_data_file),
            os.path.dirname(self.log_file),
        ]

    # ---------------------------------------------------------------------------
    def test_write_permission(self, folder: str) -> bool:
        """Test if a folder has write permission."""

        if not os.access(folder, os.W_OK):
            print(
                f"Warning: Folder {folder} exists but does not have write permission!"
            )
            try:
                # Create a test file to verify actual write permission
                test_file = os.path.join(folder, ".write_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                print(f"Write test successful despite access check failure in {folder}")
            except Exception as write_err:
                # This confirms we actually can't write to the folder
                print(f"Confirmed write permission error: {write_err}")

    # ---------------------------------------------------------------------------
    def test_folder(self, folder: str) -> None:
        """Test if a folder exists and has write permission. Creates the folder if needed."""
        try:
            # Try to create the folder directly
            os.makedirs(folder)
            print(f"Created folder: {folder}")
        except FileExistsError:
            # Folder already exists, which is fine
            pass
        except Exception as e:
            # Other creation errors (permissions, disk full, etc.)
            print(f"Error creating folder {folder}: {e}")

        self.test_write_permission(folder)

    # ---------------------------------------------------------------------------
    def test_required_paths(self) -> None:
        """Test if all required folders exist and have write permission."""
        for folder in self.required_paths:
            self.test_folder(folder)

    # ---------------------------------------------------------------------------
    def get_port(self, port: int) -> None:
        """Get an available port for the server.

        :param port: Preferred port to start the search.
        :raises ValueError: If no available port is found.
        """

        port = pt.get_port(preferred_port=port)
        if port is None:
            raise ValueError("No available port found")

        self.port = port

    # ---------------------------------------------------------------------------
    def save_server_data(self) -> None:
        """Save server data to a JSON file."""
        data = {"port": self.port}
        try:
            with open(self.server_data_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving server data: {e}")

    # ---------------------------------------------------------------------------
    def clean_server_data(self) -> None:
        """Remove the server data file."""
        try:
            os.remove(self.server_data_file)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error removing server data file: {e}")


# Initialize the server environment
env = ServerEnv()
