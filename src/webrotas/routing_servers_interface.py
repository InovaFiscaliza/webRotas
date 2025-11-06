#!/usr/bin/env python3
"""
Módulo de suporte à execução e manutenção do servidor OSRM (Open Source Routing Machine)
utilizando containers Podman, com manipulação de arquivos OSM, cache geográfico e controle
de recursos.

Este módulo oferece funções para:
- Inicializar e carregar imagens Podman necessárias para execução do OSRM.
- Processar regiões geográficas com Osmosis e preparar dados para roteamento.
- Criar e manter cache de dados OSM baseado em limites geográficos (bounding boxes).
- Gerar índices de roteamento (via `osrm-extract`, `osrm-partition`, `osrm-customize`).
- Iniciar e verificar a operação do servidor OSRM.
- Manter diretórios e contêineres limpos e atualizados.
- Encerrar processos ou contêineres antigos automaticamente.
- Manipular arquivos e diretórios de forma segura no sistema de arquivos.

Principais dependências externas:
- `podman` (containers)
- `osmosis` (filtro de dados OSM)
- `osrm-backend` (servidor de roteamento)
- `webRota` (módulo auxiliar com logging e dados do usuário)
- `project_folders` (definições de caminhos no sistema de arquivos)
- `CacheBoundingBox` (gerenciador de chaves para cache geográfico)

Exemplos de uso:
    Gerar e ativar servidor OSRM para determinada região:
        GerarIndicesExecutarOSRMServer(lista_de_regioes)

    Verificar se servidor está ativo:
        VerificarOsrmAtivo()

    Limpeza periódica:
        manutencao_arquivos_antigos()

Autor: [Seu Nome ou Equipe]
Data: [Opcional]
"""

###########################################################################################################################
import os
import shutil
import psutil
import filecmp
import subprocess
import datetime
import time
import requests
import socket
import glob
from pathlib import Path
import json
import webrotas.rotas as wr
import webrotas.project_folders as pf
import webrotas.cache.bounding_boxes as cb
import webrotas.regions as rg
import webrotas.shapefiles as sf
from webrotas.config.logging_config import get_logger

# Configure logging
logger = get_logger(__name__)


CONFIG_FILE = (
    pf.PROJECT_PATH / "src" / "backend" / "webdir" / "config" / "containers.json"
)


# -----------------------------------------------------------------------------------#
def find_available_port(start_port=50000, max_port=65535, host=None):
    """
    Procura a primeira porta disponível no host local a partir de uma porta inicial.

    Args:
        start_port (int): Porta inicial para começar a busca.
        max_port (int): Número máximo de porta a verificar (default: 65535).
        host (str): Host to bind to (default: localhost for development binding)

    Returns:
        int: O número da primeira porta disponível.

    Raises:
        RuntimeError: Se nenhuma porta estiver disponível no intervalo.
    """
    if host is None:
        host = "localhost"

    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Tenta vincular o socket à porta
                s.bind((host, port))
                return port  # Retorna a porta se estiver disponível
            except OSError:
                continue  # Porta está em uso, passa para a próxima

    raise RuntimeError(
        f"Nenhuma porta livre encontrada no intervalo {start_port}-{max_port}."
    )


# -----------------------------------------------------------------------------------#
def delete_temp_folder(filtro: str) -> bool:
    try:
        if os.path.exists(filtro):
            shutil.rmtree(filtro)
            return True
        else:
            return False
    except Exception:
        return False


# -----------------------------------------------------------------------------------#
def create_temp_folder(caminho: str) -> bool:
    try:
        os.makedirs(caminho, exist_ok=True)
        return True
    except Exception:
        return False


# -----------------------------------------------------------------------------------#
def move_files(origem: str, destino: str) -> bool:
    try:
        os.makedirs(destino, exist_ok=True)
        shutil.move(origem, destino)
        return True
    except Exception:
        return False


################################################################################
def init_and_load_podman_images():
    logger.debug("Initializing and loading podman images")

    subprocess.run(
        ["podman", "machine", "init"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    subprocess.run(
        ["podman", "machine", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(
        ["podman", "load", "-i", Path(f"{pf.OSMOSIS_PATH}") / "osmosis_webrota.tar"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(
        ["podman", "load", "-i", Path(f"{pf.OSMR_PATH}") / "data" / "osmr_webrota.tar"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


################################################################################
def FiltrarRegiaoComOsmosis(regioes):
    chave = cb.cCacheBoundingBox.chave(regioes)

    destino = Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}"
    # Se o diretório de destino já existe, não faz nada, pode ser um cache já feito corrompido, vale tentar poupar o tempo.
    if destino.exists():
        logger.info(f"Diretório '{destino}' já existe. Ignorando processamento.")
        return 0  # Não criou diretório pode ignorar criação dos indices OSMR

    logger.debug(
        f"Fazendo osmosis no diretório {pf.OSMOSIS_TEMPDATA_PATH}/filtro_{chave}"
    )

    delete_temp_folder(Path(f"{pf.OSMOSIS_TEMPDATA_PATH}") / f"filtro_{chave}")
    create_temp_folder(Path(f"{pf.OSMOSIS_TEMPDATA_PATH}") / f"filtro_{chave}")
    subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "-m",
            "32g",
            "-v",
            f"{pf.OSMOSIS_PATH}:/data",
            "--name",
            f"osmosis_{wr.UserData.ssid}",
            "localhost/osmosis_webrota",
            "osmosis",
            "--read-pbf",
            "file=/data/brazil/brazil-latest.osm.pbf",
            "--bounding-polygon",
            f"file=/data/TempData/exclusion_{chave}.poly",
            "completeWays=no",
            "--write-pbf",
            f"file=/data/TempData/filtro_{chave}/filtro-latest.osm.pbf",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    delete_temp_folder(Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}")
    create_temp_folder(Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}")

    move_files(
        Path(f"{pf.OSMOSIS_TEMPDATA_PATH}")
        / f"filtro_{chave}"
        / "filtro-latest.osm.pbf",
        Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}",
    )
    delete_temp_folder(Path(f"{pf.OSMOSIS_TEMPDATA_PATH}") / f"filtro_{chave}")
    return 1  # Criou diretório roda ciração dos indices OSMR


################################################################################
def region_container_alive(cacheid):
    containers = get_container_by_cacheid(cacheid)

    if not containers:
        # não encontrou nenhum container com esse cacheid
        logger.debug(f"Nenhum contêiner encontrado para cacheid {cacheid}")
        return None

    # se há pelo menos um container, pegue a porta do primeiro
    container_id, created_at, porta = containers[0]
    logger.debug(
        f"Contêiner {container_id} (criado em {created_at}) está na porta {porta}"
    )
    return porta


################################################################################
# def AtivaServidorOSMR(regioes):
#     return  # TODO: remover esta linha quando for usar
#     # startserver filtro 8001 osmr_server8001
#     chave = cb.cCacheBoundingBox.chave(regioes)
#     # -------------------------------------------------
#     porta = region_container_alive(chave)

#     if porta:
#         wr.UserData.OSMRport = porta
#         return

#     # -------------------------------------------------
#     wr.UserData.OSMRport = find_available_port(start_port=50000, max_port=65535)
#     logger.debug(
#         f"Porta tcp/ip disponivel encontrada: {wr.UserData.OSMRport}"
#     )
#     logger.debug("Ativando Servidor OSMR")
#     subprocess.run(
#         ["podman", "stop", f"osmr_{wr.UserData.ssid}_{chave}"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     # Assegura que o container executa em paralelo com o python
#     volume_host = str(Path(pf.OSMR_PATH_CACHE_DATA) / f"filtro_{chave}")
#     volume_container = f"/data/filtro_{chave}"
#     port_map = f"{wr.UserData.OSMRport}:5000"
#     log_file = open(logok_osmr, "a")

#     comando = f"""podman run --tty=false --rm --name osmr_{wr.UserData.ssid}_{chave} -m 32g -t -i \
#     -p {port_map} \
#     -v "{volume_host}:{volume_container}" \
#     localhost/osmr_webrota osrm-routed --algorithm mld {volume_container}/filtro-latest.osm.pbf"""

#     subprocess.Popen(comando, shell=True, stdout=log_file, stderr=subprocess.STDOUT)
#     return


################################################################################
# def GerarIndicesExecutarOSRMServer(regioes):
#     # os.chdir("../../resources/OSMR/data")
#     chave = cb.cCacheBoundingBox.chave(regioes)
#     DIRETORIO_REGIAO = Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}"
#     DIRETORIO_REGIAO_CONTAINER = f"filtro_{chave}"
#     subprocess.run(
#         ["podman", "stop", f"osmr_{wr.UserData.ssid}_{chave}"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     subprocess.run(
#         [
#             "podman",
#             "run",
#             "--rm",
#             "--name",
#             f"temp1{chave}",
#             "-m",
#             "32g",
#             "-t",
#             "-v",
#             f"{DIRETORIO_REGIAO}:/data/{DIRETORIO_REGIAO_CONTAINER}",
#             "localhost/osmr_webrota",
#             "osrm-extract",
#             "-p",
#             "/opt/car.lua",
#             f"/data/{DIRETORIO_REGIAO_CONTAINER}/filtro-latest.osm.pbf",
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     subprocess.run(
#         [
#             "podman",
#             "run",
#             "--rm",
#             "--name",
#             f"temp2{chave}",
#             "-m",
#             "32g",
#             "-t",
#             "-v",
#             f"{DIRETORIO_REGIAO}:/data/{DIRETORIO_REGIAO_CONTAINER}",
#             "localhost/osmr_webrota",
#             "osrm-partition",
#             f"/data/{DIRETORIO_REGIAO_CONTAINER}/filtro-latest.osm.pbf",
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     subprocess.run(
#         [
#             "podman",
#             "run",
#             "--rm",
#             "--name",
#             f"temp3{chave}",
#             "-m",
#             "32g",
#             "-t",
#             "-v",
#             f"{DIRETORIO_REGIAO}:/data/{DIRETORIO_REGIAO_CONTAINER}",
#             "localhost/osmr_webrota",
#             "osrm-customize",
#             f"/data/{DIRETORIO_REGIAO_CONTAINER}/filtro-latest.osm.pbf",
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     AtivaServidorOSMR(regioes)
#     return


# ################################################################################
# def manutencao_arquivos_antigos():
#     DeleteOldFilesAndFolders(f"{pf.OSMR_PATH_CACHE_DATA}", days=365)
#     DeleteOldFilesAndFolders("logs", days=30)
#     DeleteOldFilesAndFolders(pf.OSMOSIS_TEMPDATA_PATH, days=365)
#     StopOldContainers(days=30)


# ################################################################################
# def is_podman_running_health():
#     """
#     Checks whether Podman is operational and capable of running containers.

#     Returns:
#         (bool, str): A tuple where the first element indicates success (True/False),
#                      and the second element provides a descriptive status message.
#     """
#     try:
#         subprocess.run(
#             ["podman", "ps"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             check=True,
#         )
#         return True, "Podman is running and operational."

#     except FileNotFoundError:
#         return (
#             False,
#             "The 'podman' command was not found. Please ensure it is installed and in your PATH.",
#         )

#     except subprocess.CalledProcessError as e:
#         return (
#             False,
#             f"Podman returned an error.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}",
#         )

#     except Exception as e:
#         return False, f"Unexpected error: {str(e)}"


# ################################################################################
# def get_containers():
#     """
#     Obtém a lista de contêineres cujo nome começa com 'osmr_', incluindo o ID e a data de criação.
#     Retorna uma lista de tuplas (container_id, created_at).
#     """

#     subprocess.run(
#         ["podman", "machine", "start"],
#         capture_output=True,
#         text=True,
#     )

#     # Usa delimitador claro entre os campos para evitar problemas com espaços
#     result = subprocess.run(
#         ["podman", "ps", "-a", "--format", "{{.ID}}||{{.CreatedAt}}||{{.Names}}"],
#         capture_output=True,
#         text=True,
#     )

#     if result.returncode != 0:
#         return []

#     containers = []
#     for line in result.stdout.strip().splitlines():
#         parts = line.split("||")
#         if len(parts) == 3:
#             container_id, created_at, name = [p.strip() for p in parts]
#             if name.startswith("osmr_"):
#                 containers.append((container_id, created_at))

#     return containers


# ################################################################################
# def get_container_by_cacheid(cacheid):
#     """
#     Retorna uma lista com o contêiner cujo nome começa com 'osmr_' e contém o cacheid.
#     Para cada contêiner, inclui: (container_id, created_at, porta)
#     """

#     result = subprocess.run(
#         ["podman", "ps", "-a", "--format", "{{.ID}}||{{.CreatedAt}}||{{.Names}}"],
#         capture_output=True,
#         text=True,
#     )

#     if result.returncode != 0:
#         # wl.wLog("Erro ao listar contêineres")
#         return []

#     containers = []
#     for line in result.stdout.strip().splitlines():
#         parts = line.split("||")
#         if len(parts) == 3:
#             container_id, created_at, name = [p.strip() for p in parts]
#             if name.startswith("osmr_") and cacheid in name:
#                 port_result = subprocess.run(
#                     ["podman", "port", container_id],
#                     capture_output=True,
#                     text=True,
#                 )
#                 if port_result.returncode == 0:
#                     raw_port = (
#                         port_result.stdout.strip().splitlines()[0]
#                         if port_result.stdout.strip()
#                         else "desconhecida"
#                     )
#                     if "->" in raw_port and ":" in raw_port:
#                         porta = raw_port.split(":")[
#                             -1
#                         ]  # pega só a última parte (ex: 50000)
#                     else:
#                         porta = raw_port
#                 else:
#                     porta = "erro"

#                 containers.append((container_id, created_at, porta))

#     return containers


###########################################################################################################################
def check_osrm_server(host: str, port: int, timeout: int = 3) -> bool:
    """Verifica se o servidor OSRM está ativo, consultando /health ou root."""
    url = f"http://{host}:{port}/health"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            url = "http://{host}:{port}/route/v1/driving/-51.512533,-29.972345;-51.724061,-30.036089?overview=full&geometries=polyline&steps=true"
            logger.debug(url)

            response = requests.get(url)
            data = response.json()
            if response.status_code == 200 and "routes" in data:
                return True
    except requests.exceptions.RequestException:
        return False
    return False


###########################################################################################################################
# def start_or_find_server_for_this_route(start_lat, start_lon, end_lat, end_lon):
#     cache, regioes = cb.cCacheBoundingBox.find_server_for_this_route(
#         start_lat, start_lon, end_lat, end_lon
#     )
#     if cache == None:
#         wl.wLog(
#             f"Não encontrada região no cache para essa rota - id: {cache}",
#             level="debug",
#         )
#         return False
#     wl.wLog(f"Ativando região para essa rota: {cache}", level="debug")
#     AtivaServidorOSMR(regioes)

#     osrm_port = None
#     while osrm_port == None:
#         time.sleep(1)
#         osrm_port = region_container_alive(cache)

#         if osrm_port:
#             wr.UserData.OSMRport = porta
#             if check_osrm_server("localhost", porta, 3):
#                 wl.wLog(
#                     f"Servidor iniciado - id: {cache} -  ({start_lat}, {start_lon}), ({end_lat}, {end_lon})"
#                 )
#                 return True


################################################################################
# def get_max_active_containers():
#     """
#     Carrega o número máximo de contêineres permitidos em execução a partir do arquivo JSON.
#     Retorna 5 se não conseguir carregar.
#     """
#     try:
#         with open(CONFIG_FILE, "r") as f:
#             config = json.load(f)
#             return int(config.get("max_active_containers", 5))
#     except Exception:
#         return 5


################################################################################
# def keep_last_n_containers_running():
#     """
#     Mantém apenas os contêineres mais recentes definidos no JSON em execução.
#     """
#     num_max = get_max_active_containers()
#     containers = get_containers()
#     now = datetime.datetime.now()

#     def parse_created_time(created_at):
#         try:
#             cleaned = " ".join(created_at.split()[:2])[:26]
#             return datetime.datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S.%f")
#         except ValueError:
#             return now  # Se falhar, assume como se fosse "agora"

#     containers_sorted = sorted(
#         containers, key=lambda c: parse_created_time(c[1]), reverse=True
#     )

#     ids_to_keep = {c[0] for c in containers_sorted[: num_max - 1]}

#     result = subprocess.run(
#         ["podman", "ps", "--format", "{{.ID}}"],
#         capture_output=True,
#         text=True,
#     )
#     running_ids = set(result.stdout.strip().splitlines())

#     for container_id in running_ids:
#         if container_id not in ids_to_keep:
#             logger.info(f"Parando conteiner: {container_id}")
#             subprocess.run(["podman", "stop", container_id], stdout=subprocess.DEVNULL)


################################################################################
# def StopOldContainers(days=30):
#     """
#     Para contêineres que têm mais de 'days' dias de idade.
#     """
#     # Obtém a data atual
#     current_time = datetime.datetime.now()

#     # Obtém os contêineres
#     containers = get_containers()

#     for container_id, created_at in containers:
#         # Converte a data de criação para um objeto datetime
#         try:
#             # Remover a parte extra do fuso horário (a última parte)
#             created_at_cleaned = (
#                 created_at.split(" ")[0] + " " + created_at.split(" ")[1]
#             )  # Remove a parte extra de fuso horário
#             created_at_cleaned = created_at_cleaned[:26]
#             # wLog("---------------------- Data com problema "+created_at_cleaned)
#             created_time = datetime.datetime.strptime(
#                 created_at_cleaned, "%Y-%m-%d %H:%M:%S.%f"
#             )
#         except ValueError:
#             # Caso o formato de data não tenha microsegundos
#             created_at_cleaned = (
#                 created_at.split(" ")[0] + " " + created_at.split(" ")[1]
#             )  # Remove a parte extra de fuso horário
#             created_at_cleaned = created_at_cleaned[:26]
#             # wLog("---------------------- Data ajustada "+created_at_cleaned)
#             created_time = datetime.datetime.strptime(
#                 created_at_cleaned, "%Y-%m-%d %H:%M:%S.%f"
#             )

#         # Calcula a diferença de dias entre a data atual e a data de criação
#         age_in_days = (current_time - created_time).days
#         # wLog(f"---------------------- age_in_days: {age_in_days}")

#         # Se o contêiner for mais antigo que o limite (30 dias)
#         if age_in_days > days:
#             logger.info(f"Parando contêiner {container_id} (idade: {age_in_days} dias)")
#             subprocess.run(["podman", "stop", container_id])


################################################################################
def VerificarOsrmAtivo(tentativas=1000, intervalo=5):
    """
    Verifica se o servidor OSRM está ativo.

    Args:
    - tentativas: Número máximo de tentativas de verificação.
    - intervalo: Intervalo de tempo (em segundos) entre as tentativas.

    Returns:
    - bool: True se o servidor estiver no ar, False caso contrário.
    """
    from webrotas.config.server_hosts import get_osrm_host

    osrm_host = get_osrm_host()
    url = f"http://{osrm_host}:{UserData.OSMRport}/route/v1/driving/-43.105772903105354,-22.90510838815471;-43.089637952126694,-22.917360518277434?overview=full&geometries=polyline&steps=true"

    for tentativa in range(tentativas):
        try:
            # Faz a requisição GET
            response = requests.get(url)

            # Verifica o código de status HTTP
            if response.status_code == 200:
                logger.debug("OSRM está funcionando corretamente.")
                return True
            else:
                logger.debug(
                    f"Tentativa {tentativa + 1}/{tentativas}: Erro {response.status_code}. Tentando novamente..."
                )
                if VerificarFalhaServidorOSMR():
                    return False

        except requests.exceptions.RequestException as e:
            logger.debug(
                f"Tentativa {tentativa + 1}/{tentativas}: Erro ao acessar o OSRM: {e}. Tentando novamente..."
            )
            if VerificarFalhaServidorOSMR():
                return False

        # Aguarda o intervalo antes de tentar novamente
        time.sleep(intervalo)

    logger.debug("O servidor OSRM não ficou disponível após várias tentativas.")
    return False


################################################################################
# def procurar_multiplas_strings_em_arquivo(caminho_arquivo, lista_strings):
#     try:
#         with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
#             for linha in arquivo:
#                 for s in lista_strings:
#                     if s in linha:
#                         return True
#         return False
#     except FileNotFoundError:
#         logger.warning(f"Arquivo não encontrado: {caminho_arquivo}")
#         return False
#     except Exception as e:
#         logger.error(f"Erro ao ler o arquivo: {e}")
#         return False


################################################################################
# def VerificarFalhaServidorOSMR():
#     # TODO: Implement proper log file location if needed
#     # For now, we'll skip file-based error checking
#     logger.debug("Verificando falhas do servidor OSRM")
#     return False


################################################################################
# def KillProcessByCommand(target_command):
#     """
#     Encerra processos com base em um comando específico.

#     :param target_command: Parte do comando que identifica o processo a ser encerrado (string).
#     """
#     found = False  # Para verificar se algum processo foi encontrado
#     for process in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
#         try:
#             # Obtém a linha de comando do processo
#             cmdline = process.info["cmdline"]
#             # Verifica se cmdline não é None e contém o comando alvo
#             if cmdline and target_command in cmdline:
#                 logger.info(
#                     f"Matando processo {process.info['name']} (PID: {process.info['pid']})"
#                 )
#                 process.kill()  # Encerra o processo
#                 found = True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass

#     if not found:
#         # wLog(f"Nenhum processo encontrado com o comando '{target_command}'.")
#         pass
#     else:
#         # wLog("Processo encerrado com sucesso, se encontrado.")
#         pass


################################################################################
# def MataServidorWebRotas():
#     KillProcessByCommand("Server.py")
#     return


################################################################################
# def VerificaArquivosIguais(arquivo_atual, arquivo_backup):
#     # Verifica se ambos os arquivos existem
#     if not os.path.exists(arquivo_atual):
#         logger.warning(f"O arquivo atual '{arquivo_atual}' não existe.")
#         return False
#     if not os.path.exists(arquivo_backup):
#         logger.warning(f"O arquivo backup '{arquivo_backup}' não existe.")
#         return False

#     # Compara os arquivos
#     arquivos_sao_iguais = filecmp.cmp(arquivo_atual, arquivo_backup, shallow=False)
#     return arquivos_sao_iguais


###########################################################################################################################
# def DeleteOldFilesAndFolders(directory, days=30):
#     """
#     Remove arquivos e pastas (inclusive não vazias) mais antigos que um número específico de dias.

#     Args:
#         directory (str): Caminho para o diretório base.
#         days (int): Número de dias para considerar como o limite. Padrão é 30.

#     DeleteOldFilesAndFolders("/caminho/para/seu/diretorio", days=30)
#     """
#     try:
#         # Calcula a data limite
#         now = time.time()
#         cutoff = now - (days * 86400)  # 86400 segundos por dia

#         # Itera pelos itens no diretório
#         for filename in os.listdir(directory):
#             item_path = os.path.join(directory, filename)

#             # Obtém o tempo de modificação do item
#             item_mtime = os.path.getmtime(item_path)

#             # Verifica se é um arquivo
#             if os.path.isfile(item_path) and item_mtime < cutoff:
#                 os.remove(item_path)
#                 logger.debug(f"Arquivo removido: {item_path}")

#             # Verifica se é um diretório
#             elif os.path.isdir(item_path) and item_mtime < cutoff:
#                 # Remove o diretório e todo o seu conteúdo
#                 shutil.rmtree(item_path)  # Remove diretórios e seus conteúdos
#                 logger.debug(f"Pasta removida: {item_path}")
#     except Exception as e:
#         logger.error(f"Erro ao processar o diretório: {e}")


################################################################################
# def parar_containers_osmr(nome_usuario):
#     try:
#         # Lista os containers com nome
#         podman_ps = subprocess.run(
#             ["podman", "ps", "-a", "--format", "{{.ID}} {{.Names}}"],
#             capture_output=True,
#             text=True,
#             check=True,
#         )

#         linhas = podman_ps.stdout.strip().splitlines()
#         for linha in linhas:
#             container_id, container_name = linha.strip().split(maxsplit=1)
#             # if container_name == f"osmr_{nome_usuario}":
#             if container_name.startswith(f"osmr_{nome_usuario}_"):
#                 subprocess.run(
#                     ["podman", "stop", container_id],
#                     stdout=subprocess.DEVNULL,
#                     stderr=subprocess.DEVNULL,
#                 )
#                 logger.debug(f"Container {container_name} parado.")

#     except Exception as e:
#         logger.error(f"Erro ao parar containers: {e}")


################################################################################
# def recreate_temp_folders_osmr():
#     logger.debug("Removendo arquivos osmozis e osmr")

#     caminhos = [f"../../resources/Osmosis/TempData/exclusion_{wr.UserData.ssid}*"]

#     for caminho in caminhos:
#         for item in glob.glob(caminho, recursive=True):
#             try:
#                 if os.path.isfile(item):
#                     os.remove(item)
#                     logger.debug(f"Arquivo removido: {item}")
#                 elif os.path.isdir(item):
#                     shutil.rmtree(item)
#                     logger.debug(f"Diretório removido: {item}")
#             except Exception as e:
#                 logger.error(f"Erro ao remover {item}: {e}")


################################################################################
# def esperar_container_parar(nome_usuario, timeout=30):
#     for _ in range(timeout):
#         # Verifica se o container ainda está rodando
#         result = subprocess.run(
#             ["podman", "ps", "--filter", f"name={nome_usuario}", "--format", "{{.ID}}"],
#             capture_output=True,
#             text=True,
#         )
#         if not result.stdout.strip():
#             return  # Container finalizou
#         time.sleep(1)
#     raise TimeoutError(
#         f"Container de {nome_usuario} ainda está ativo após {timeout} segundos."
#     )


################################################################################
# def limpar_cache_files_osmr(regioes):
#     try:
#         wl.wLog(
#             f"Parando todos os containers osmr do usário {wr.UserData.ssid}",
#             level="debug",
#         )
#         parar_containers_osmr(wr.UserData.ssid)
#         esperar_container_parar(wr.UserData.ssid)
#         wl.wLog("Apagando arquivo de log...", level="debug")
#         log_filename = wl.get_log_filename()
#         log_file = f"{log_filename}.{wr.UserData.ssid}.OSMR"
#         backup_file = log_file + ".LastError"
#         try:
#             if os.path.exists(log_file):
#                 shutil.copy(log_file, backup_file)
#                 wl.wLog(f"Cópia de segurança criada: {backup_file}", level="debug")
#             os.remove(log_file)
#             wl.wLog(f"Removido: {log_file}", level="debug")
#         except FileNotFoundError:
#             wl.wLog(f"Arquivo não encontrado: {log_file}")
#         except Exception as e:
#             wl.wLog(f"Erro ao remover {log_file}: {e}")
#         remover_arquivos_osmr()
#         wl.wLog("Limpeza concluída com sucesso.", level="debug")
#     except Exception as e:
#         wl.wLog(f"Erro durante a limpeza dos caches : {e}")

#     cb.cCacheBoundingBox.delete(regioes)


################################################################################
def PreparaServidorRoteamento(routing_area):
    roteamento_ok = False

    # Get cache ID for this routing area
    cache_id = cb.cCacheBoundingBox.chave(routing_area)

    while not roteamento_ok:
        if (
            cb.cCacheBoundingBox.get_cache(routing_area) is None
        ):  # servidor não tem cache ID
            wr.GeraArquivoExclusoes(
                routing_area,
                arquivo_saida=Path(f"{pf.OSMOSIS_TEMPDATA_PATH}")
                / f"exclusion_{cb.cCacheBoundingBox.chave(routing_area)}.poly",
            )
            cb.cCacheBoundingBox.route_cache_clear_regioes()
            logger.debug("FiltrarRegiãoComOsmosis")
            if FiltrarRegiaoComOsmosis(routing_area) == 1:
                logger.debug("GerarIndicesExecutarOSRMServer")
                GerarIndicesExecutarOSRMServer(routing_area)
            else:
                logger.debug(
                    "Dados de roteamento encontrados no diretorio filtro OSMR cache, ativando o servidor OSMR"
                )
                # AtivaServidorOSMR(routing_area)  # TODO: Remover isso
            info_regiao = sf.ObterMunicipiosNoBoundingBoxOrdenados(
                rg.extrair_bounding_box_de_regioes(routing_area)
            )
            km2_região = wr.calc_km2_regiao(routing_area)
            cb.cCacheBoundingBox.new(
                routing_area,
                f"filtro_{cb.cCacheBoundingBox.chave(routing_area)}",
                info_regiao,
                km2_região,
            )
        else:
            logger.debug(
                "Dados de roteamento encontrados no cache, nao e necessario executar osmosis"
            )
            # AtivaServidorOSMR(routing_area)
        if VerificarOsrmAtivo():
            roteamento_ok = True
        else:
            cache_id = cb.cCacheBoundingBox.chave(routing_area)
            logger.error(
                f"Erro de cache encontrado reiniciando geração dos mapas - id: {cache_id}"
            )
            # limpar_cache_files_osmr(routing_area)
