#!/usr/bin/env python3
"""
Script para detectar caminho do projeto e criar diretórios de cache multiplataforma
"""
import os
import platform
from pathlib import Path

PROJECT_FOLDER_NAME = "webRotas"

# ----------------------------------------------------------------------------------------------
def get_project_path(project_folder_name: str, required_depth: int = 0) -> Path:
    """
    Sobe na árvore de diretórios até encontrar a pasta com nome `project_folder_name`.
    Se houver múltiplas, pega a mais próxima que esteja na profundidade esperada (se especificado).
    """
    base_path = Path(__file__).resolve()
    matches = [p for p in base_path.parents if p.name == project_folder_name]

    if not matches:
        raise ValueError(f"Pasta '{project_folder_name}' não encontrada no caminho.")

    if required_depth > 0:
        for m in matches:
            if len(m.parts) >= required_depth:
                return m
        raise ValueError(f"Nenhuma ocorrência de '{project_folder_name}' com profundidade >= {required_depth}")
    
    # Retorna a mais próxima (primeira ocorrência subindo a árvore)
    return matches[0]

# ----------------------------------------------------------------------------------------------
PROJECT_PATH = get_project_path(PROJECT_FOLDER_NAME)

# Detecta o sistema operacional
is_windows = platform.system() == "Windows"

# Define o diretório base de cache conforme o sistema
if is_windows:
    base_cache_path = Path(os.environ.get('PROGRAMDATA')) / "ANATEL"
else:
    base_cache_path = Path.home() / ".cache" / "anatel"

# Define os caminhos finais
WINDOWS_CACHE_PATH = base_cache_path / f"{PROJECT_FOLDER_NAME}Cache"
OSMOSIS_TEMPDATA_CACHE_PATH = WINDOWS_CACHE_PATH / "Osmosis" / "TempData"
OSMOSIS_PATH_CACHE = WINDOWS_CACHE_PATH / "Osmosis" 
OSMOSIS_PATH = PROJECT_PATH / "src" / "resources" / "Osmosis"

 
# Cria os diretórios se não existirem
for path in [WINDOWS_CACHE_PATH, OSMOSIS_TEMPDATA]:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


