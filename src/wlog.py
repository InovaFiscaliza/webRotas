#!/usr/bin/env python3
"""
Módulo de logging personalizado para aplicações web com suporte à substituição de acentos.

Este módulo fornece funções para:
- Configurar o nome do arquivo de log por usuário.
- Registrar mensagens de log em níveis diferentes (info, debug, warning, error, critical).
- Imprimir logs no console com base em um nível mínimo configurável.
- Substituir caracteres acentuados por suas formas não acentuadas, útil para compatibilidade de logs.

O nome do arquivo de log final é composto por um nome base (_log_filename) seguido do nome do usuário
presente em `wr.UserData.nome`.

Dependências:
- `webRota` (importado como `wr`) deve fornecer `UserData.nome`.
- `datetime` e `os` da biblioteca padrão.
"""
import web_rotas as wr
import datetime
import os

# ---------------------------------------------------------------------------------------------
WARNING_LEVEL = "info"
_log_filename = "webRotasServer.log"  # Agora com underline → uso interno


# ---------------------------------------------------------------------------------------------
def set_log_filename(filename):
    global _log_filename
    _log_filename = filename


# ---------------------------------------------------------------------------------------------
def get_log_filename():
    return _log_filename


# ---------------------------------------------------------------------------------------------
def wLog(log_string, level="info"):
    print(log_string)


# ---------------------------------------------------------------------------------------------
def SubstAcentos(texto: str) -> str:
    """
    Substitui caracteres acentuados por suas versões sem acento.

    :param texto: Texto de entrada possivelmente com acentos.
    :return: Texto sem acentuação.
    """
    mapeamento = {
        # Letras minúsculas
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "í": "i",
        "ì": "i",
        "î": "i",
        "ï": "i",
        "ó": "o",
        "ò": "o",
        "õ": "o",
        "ô": "o",
        "ö": "o",
        "ú": "u",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
        "ñ": "n",
        # Letras maiúsculas
        "Á": "A",
        "À": "A",
        "Ã": "A",
        "Â": "A",
        "Ä": "A",
        "É": "E",
        "È": "E",
        "Ê": "E",
        "Ë": "E",
        "Í": "I",
        "Ì": "I",
        "Î": "I",
        "Ï": "I",
        "Ó": "O",
        "Ò": "O",
        "Õ": "O",
        "Ô": "O",
        "Ö": "O",
        "Ú": "U",
        "Ù": "U",
        "Û": "U",
        "Ü": "U",
        "Ç": "C",
        "Ñ": "N",
    }

    return "".join(mapeamento.get(char, char) for char in texto)


# ---------------------------------------------------------------------------------------------
