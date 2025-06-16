import webRota as wr
import datetime
import os

################################################################################
WARNING_LEVEL = "info"
_log_filename = "WebRotasServer.log"  # Agora com underline → uso interno

def set_log_filename(filename):
    global _log_filename
    _log_filename = filename

def get_log_filename():
    return _log_filename

# from wlog import log_filename
# from wlog import wLog

def wLog(log_string, level="info"):  # Levels "info","debug", "warning", "error", "critical"
    levels = {"info": 1, "debug": 2, "warning": 3, "error": 4, "critical": 5}
    current_level = levels.get(level.lower(), 0)

    log_file = f"{_log_filename}.{wr.UserData.nome}"  # Nome do arquivo de log

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

################################################################################
def SubstAcentos(texto):
    """
    Substitui caracteres acentuados por suas versões sem acento.
    """
    mapeamento = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "ä": "a",
        "Á": "A",
        "À": "A",
        "Ã": "A",
        "Â": "A",
        "Ä": "A",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "É": "E",
        "È": "E",
        "Ê": "E",
        "Ë": "E",
        "í": "i",
        "ì": "i",
        "î": "i",
        "ï": "i",
        "Í": "I",
        "Ì": "I",
        "Î": "I",
        "Ï": "I",
        "ó": "o",
        "ò": "o",
        "õ": "o",
        "ô": "o",
        "ö": "o",
        "Ó": "O",
        "Ò": "O",
        "Õ": "O",
        "Ô": "O",
        "Ö": "O",
        "ú": "u",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "Ú": "U",
        "Ù": "U",
        "Û": "U",
        "Ü": "U",
        "ç": "c",
        "Ç": "C",
        "ñ": "n",
        "Ñ": "N",
    }

    # Substitui cada caractere com base no mapeamento
    for acentuado, sem_acento in mapeamento.items():
        texto = texto.replace(acentuado, sem_acento)

    return texto
################################################################################