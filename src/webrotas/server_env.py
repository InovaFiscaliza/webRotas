"""Server environment configuration"""

import json
from pathlib import Path
from typing import Optional
import webrotas.port_test as pt

# Module directory (where this file is located)
MODULE_DIR = Path(__file__).parent

# Default configuration
DEFAULT_PORT = 5002
DEFAULT_DEBUG = False


class ServerEnv:
    """Manages server environment configuration and paths."""
    
    def __init__(self):
        self.port: int = DEFAULT_PORT
        self.debug_mode: bool = DEFAULT_DEBUG
        
        # Paths relative to module directory
        self.log_file = MODULE_DIR / "logs" / "webRotas"
        self.server_data_file = MODULE_DIR / "config" / "server.json"
        
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        for path in [self.log_file, self.server_data_file]:
            path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_port(self, preferred_port: int) -> None:
        """Get an available port, starting from the preferred port."""
        port = pt.get_port(preferred_port=preferred_port)
        if port is None:
            raise ValueError("No available port found")
        self.port = port
    
    def save_server_data(self) -> None:
        """Save server configuration to JSON file."""
        data = {"port": self.port}
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
