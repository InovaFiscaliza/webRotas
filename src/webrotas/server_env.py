"""Server environment configuration"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Module directory (where this file is located)
MODULE_DIR = Path(__file__).parent.parent.parent

# Default configuration
DEFAULT_WEBROTAS_PORT = 5002
DEFAULT_OSRM_PORT = 5000
DEFAULT_DEBUG = False


class ServerEnv:
    """Manages server environment configuration and paths."""

    def __init__(self):
        # Read ports from environment variables (set by .env file)
        self.webrotas_port: int = int(os.getenv("WEBROTAS_PORT", DEFAULT_WEBROTAS_PORT))
        self.osrm_port: int = int(os.getenv("OSRM_PORT", DEFAULT_OSRM_PORT))
        self.debug_mode: bool = DEFAULT_DEBUG

        # Paths relative to module directory
        self.log_file = MODULE_DIR / "logs" / "webRotas"
        self.server_data_file = MODULE_DIR / "config" / "server.json"

        self._ensure_directories()

    @property
    def port(self) -> int:
        """Get the webRotas server port."""
        return self.webrotas_port

    @port.setter
    def port(self, value: int) -> None:
        """Set the webRotas server port."""
        self.webrotas_port = value

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        for path in [self.log_file, self.server_data_file]:
            path.parent.mkdir(parents=True, exist_ok=True)

    def save_server_data(self) -> None:
        """Save server configuration to JSON file."""
        data = {"webrotas_port": self.webrotas_port, "osrm_port": self.osrm_port}
        try:
            with self.server_data_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving server data: {e}")

    def clean_server_data(self) -> None:
        """Remove server configuration file."""
        try:
            self.server_data_file.unlink(missing_ok=True)
        except Exception as e:
            print(f"Error removing server data file: {e}")


# Initialize the server environment
env = ServerEnv()
