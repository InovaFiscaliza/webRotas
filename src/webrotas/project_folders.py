"""
Script para detectar caminho do projeto e criar diretórios de cache multiplataforma
"""

import os
import platform
from pathlib import Path

PROJECT_PATH = Path(__file__).parents[2]

# Detecta o sistema operacional
is_windows = platform.system() == "Windows"

# Define o diretório base de cache conforme o sistema echo %PROGRAMDATA%
if is_windows:
    base_cache_path = Path(os.environ.get("PROGRAMDATA")) / "ANATEL"
else:
    base_cache_path = Path.home() / ".cache" / "anatel"

# Define os caminhos finais
LOGS_PATH = PROJECT_PATH / "logs"

WINDOWS_CACHE_PATH = base_cache_path / f"{PROJECT_PATH.stem}Cache"
OSMOSIS_PATH = PROJECT_PATH / "resources" / "Osmosis"
OSMOSIS_TEMPDATA_PATH = PROJECT_PATH / "resources" / "Osmosis" / "TempData"
OSMOSIS_BRAZIL_PATH = PROJECT_PATH / "resources" / "Osmosis" / "brazil"

OSMR_PATH = PROJECT_PATH / "resources" / "OSMR"
OSMR_PATH_CACHE = WINDOWS_CACHE_PATH
OSMR_PATH_CACHE_DATA = WINDOWS_CACHE_PATH


# Cria os diretórios se não existirem
for path in [
    LOGS_PATH,
    WINDOWS_CACHE_PATH,
    OSMOSIS_PATH,
    OSMOSIS_TEMPDATA_PATH,
    OSMOSIS_BRAZIL_PATH,
    OSMR_PATH,
    OSMR_PATH_CACHE,
    OSMR_PATH_CACHE_DATA,
]:
    path.mkdir(parents=True, exist_ok=True)
