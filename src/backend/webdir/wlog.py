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
import webRota as wr
import datetime
import os

# ---------------------------------------------------------------------------------------------
WARNING_LEVEL = "info"
_log_filename = "WebRotasServer.log"  # Agora com underline → uso interno


# ---------------------------------------------------------------------------------------------
def set_log_filename(filename):
    global _log_filename
    _log_filename = filename


# ---------------------------------------------------------------------------------------------
def get_log_filename():
    return _log_filename


# ---------------------------------------------------------------------------------------------
def wLog(
    log_string, level="info"
):  # Levels "info","debug", "warning", "error", "critical"
    levels = {"info": 1, "debug": 2, "warning": 3, "error": 4, "critical": 5}
    current_level = levels.get(level.lower(), 0)

    log_file = f"{_log_filename}.{wr.UserData.ssid}"  # Nome do arquivo de log

    timStp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_string = SubstAcentos(log_string)
    log_string = timStp + "  " + level.ljust(7) + " : " + log_string
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(log_file):
            with open(log_file, "w") as file:
                file.write(
                    timStp + "  " + level.ljust(7) + " : " + "### Inicio do Log ###\n"
                )  # Opcional: cabeçalho inicial
        # Abre o arquivo no modo append (adicionar)
        with open(log_file, "a") as file:
            file.write(log_string + "\n")  # Escreve a mensagem com uma nova linha
        if levels.get(WARNING_LEVEL.lower(), 0) >= current_level:
            print(log_string)  # Também exibe a mensagem no console

    except Exception as e:
        print(f"Erro ao escrever no log: {e}")


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
