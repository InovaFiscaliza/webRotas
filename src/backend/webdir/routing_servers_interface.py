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

import webRota as wr
import project_folders as pf
import CacheBoundingBox as cb
import regions as rg
import shapeFiles as sf
import GuiOutput as gi

import wlog as wl

CONFIG_FILE = pf.PROJECT_PATH / "src" / "backend" / "webdir" / "containers_config.json"

################################################################################
def FindFreePort(start_port=50000, max_port=65535):
    """
    Procura a primeira porta disponível no host local a partir de uma porta inicial.

    Args:
        start_port (int): Porta inicial para começar a busca.
        max_port (int): Número máximo de porta a verificar (default: 65535).

    Returns:
        int: O número da primeira porta disponível.

    Raises:
        RuntimeError: Se nenhuma porta estiver disponível no intervalo.
    """
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Tenta vincular o socket à porta
                s.bind(("localhost", port))
                return port  # Retorna a porta se estiver disponível
            except OSError:
                continue  # Porta está em uso, passa para a próxima
    raise RuntimeError(
        f"Nenhuma porta livre encontrada no intervalo {start_port}-{max_port}."
    )


################################################################################

def remover_diretorio(filtro: str) -> bool:
    """
    Remove um diretório e todo o seu conteúdo, se ele existir.

    :param filtro: Caminho do diretório a ser removido.
    :return: True se o diretório foi removido com sucesso, False se não existia ou houve erro.
    """
    try:
        if os.path.exists(filtro):
            shutil.rmtree(filtro)  # Remove o diretório e todo o seu conteúdo
            wr.wLog(f"Diretório {filtro} removido com sucesso!", level="warning")
            return True
        else:
            wr.wLog(f"O diretório {filtro} não existe.", level="warning")
            return False
    except Exception as e:
        wr.wLog(f"Erro ao remover {filtro}: {e}")
        return False


################################################################################
def criar_diretorio(caminho: str) -> bool:
    """
    Cria um diretório de forma segura no Windows ou Linux.

    :param caminho: Caminho do diretório a ser criado.
    :return: True se o diretório foi criado ou já existia, False se houve erro.
    """
    try:
        os.makedirs(
            caminho, exist_ok=True
        )  # Cria o diretório e evita erro se já existir
        return True
    except Exception as e:
        wr.wLog(f"Erro ao criar o diretório {caminho}: {e}")
        return False


################################################################################
def mover_arquivo(origem: str, destino: str) -> bool:
    """
    Move um arquivo de uma pasta para outra.

    :param origem: Caminho do arquivo de origem.
    :param destino: Caminho do diretório de destino.
    :return: True se o arquivo foi movido com sucesso, False caso contrário.
    """
    try:
        os.makedirs(destino, exist_ok=True)  # Garante que o diretório de destino existe
        shutil.move(origem, destino)
        return True
    except Exception as e:
        wr.wLog(f"Erro ao mover {origem} para {destino}: {e}")
        return False


################################################################################
def init_and_load_podman_images():
    wr.wLog(f"init_and_load_podman_images", level="debug")
    
    log_filename = wl.get_log_filename()
    logok = f"{log_filename}.{wr.UserData.nome}.OSMR"
    subprocess.run(
        ["podman", "machine", "init"], stdout=open(logok, "a"), stderr=subprocess.STDOUT
    )
    subprocess.run(
        ["podman", "machine", "start"],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    subprocess.run(
        ["podman", "load", "-i", Path(f"{pf.OSMOSIS_PATH}") / "osmosis_webrota.tar"],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    subprocess.run(
        ["podman", "load", "-i", Path(f"{pf.OSMR_PATH}") / "data" / "osmr_webrota.tar"],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    


################################################################################
def FiltrarRegiaoComOsmosis(regioes):
    chave = cb.cCacheBoundingBox.chave(regioes)
    log_filename = wl.get_log_filename()
    logok = f"{log_filename}.{wr.UserData.nome}.OSMR"

    destino = Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}"
    # Se o diretório de destino já existe, não faz nada, pode ser um cache já feito corrompido, vale tentar poupar o tempo.
    if destino.exists():
        wr.wLog(f"Diretório '{destino}' já existe. Ignorando processamento.")
        return 0  # Não criou diretório pode ignorar criação dos indices OSMR

    wr.wLog(
        f"Fazendo osmosis no diretório {pf.OSMOSIS_TEMPDATA_PATH}/filtro_{chave}",
        level="debug",
    )

    remover_diretorio(Path(f"{pf.OSMOSIS_TEMPDATA_PATH}") / f"filtro_{chave}")
    criar_diretorio(Path(f"{pf.OSMOSIS_TEMPDATA_PATH}") / f"filtro_{chave}")
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
            f"osmosis_{wr.UserData.nome}",
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
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    remover_diretorio(Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}")
    criar_diretorio(Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}")

    mover_arquivo(
        Path(f"{pf.OSMOSIS_TEMPDATA_PATH}")
        / f"filtro_{chave}"
        / "filtro-latest.osm.pbf",
        Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}",
    )
    remover_diretorio(Path(f"{pf.OSMOSIS_TEMPDATA_PATH}") / f"filtro_{chave}")
    return 1  # Criou diretório roda ciração dos indices OSMR


################################################################################
def AtivaServidorOSMR(regioes):
    # startserver filtro 8001 osmr_server8001
    chave = cb.cCacheBoundingBox.chave(regioes)
    wr.UserData.OSMRport = FindFreePort(start_port=50000, max_port=65535)
    wr.wLog(f"Porta tcp/ip disponivel encontrada: {wr.UserData.OSMRport}", level="debug")
    log_filename = wl.get_log_filename()
    logok_osmr = f"{log_filename}.{wr.UserData.nome}.OSMR"
    wr.wLog(f"Ativando Servidor OSMR", level="info")
    subprocess.run(
        ["podman", "stop", f"osmr_{wr.UserData.nome}_{chave}"],
        stdout=open(logok_osmr, "a"),
        stderr=subprocess.STDOUT,
    )
    # Assegura que o container executa em paralelo com o python
    volume_host = str(Path(pf.OSMR_PATH_CACHE_DATA) / f"filtro_{chave}")
    volume_container = f"/data/filtro_{chave}"
    port_map = f"{wr.UserData.OSMRport}:5000"
    log_file = open(logok_osmr, "a")

    comando = f"""podman run --rm --name osmr_{wr.UserData.nome}_{chave} -m 32g -t -i \
    -p {port_map} \
    -v "{volume_host}:{volume_container}" \
    localhost/osmr_webrota osrm-routed --algorithm mld {volume_container}/filtro-latest.osm.pbf"""

    subprocess.Popen(comando, shell=True, stdout=log_file, stderr=subprocess.STDOUT)
    return


################################################################################
def GerarIndicesExecutarOSRMServer(regioes):

    # os.chdir("../../resources/OSMR/data")
    chave = cb.cCacheBoundingBox.chave(regioes)
    log_filename = wl.get_log_filename()
    logok = f"{log_filename}.{wr.UserData.nome}"
    DIRETORIO_REGIAO = Path(f"{pf.OSMR_PATH_CACHE_DATA}") / f"filtro_{chave}"
    DIRETORIO_REGIAO_CONTAINER = f"filtro_{chave}"
    subprocess.run(
        ["podman", "stop", f"osmr_{wr.UserData.nome}_{chave}"],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--name",
            f"temp1{chave}",
            "-m",
            "32g",
            "-t",
            "-v",
            f"{DIRETORIO_REGIAO}:/data/{DIRETORIO_REGIAO_CONTAINER}",
            "localhost/osmr_webrota",
            "osrm-extract",
            "-p",
            "/opt/car.lua",
            f"/data/{DIRETORIO_REGIAO_CONTAINER}/filtro-latest.osm.pbf",
        ],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--name",
            f"temp2{chave}",
            "-m",
            "32g",
            "-t",
            "-v",
            f"{DIRETORIO_REGIAO}:/data/{DIRETORIO_REGIAO_CONTAINER}",
            "localhost/osmr_webrota",
            "osrm-partition",
            f"/data/{DIRETORIO_REGIAO_CONTAINER}/filtro-latest.osm.pbf",
        ],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--name",
            f"temp3{chave}",
            "-m",
            "32g",
            "-t",
            "-v",
            f"{DIRETORIO_REGIAO}:/data/{DIRETORIO_REGIAO_CONTAINER}",
            "localhost/osmr_webrota",
            "osrm-customize",
            f"/data/{DIRETORIO_REGIAO_CONTAINER}/filtro-latest.osm.pbf",
        ],
        stdout=open(logok, "a"),
        stderr=subprocess.STDOUT,
    )
    AtivaServidorOSMR(regioes)
    return


################################################################################
def manutencao_arquivos_antigos():
    DeleteOldFilesAndFolders(f"{pf.OSMR_PATH_CACHE_DATA}", days=365)
    DeleteOldFilesAndFolders("logs", days=30)
    DeleteOldFilesAndFolders(pf.OSMOSIS_TEMPDATA_PATH, days=365)
    StopOldContainers(days=30)


################################################################################
def get_containersOLD():
    """
    Obtém a lista de contêineres, incluindo o ID e a data de criação.
    Retorna uma lista de tuplas (container_id, created_at).
    """

    subprocess.run(
        ["podman", "machine", "start"],
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["podman", "ps", "-a", "--format", "{{.ID}} {{.CreatedAt}}"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        wr.wLog("Erro ao listar contêineres")
        return []

    containers = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        container_id, created_at = parts[0], parts[1]
        containers.append((container_id, created_at))
    return containers

################################################################################
def get_containers():
    """
    Obtém a lista de contêineres cujo nome começa com 'osmr_', incluindo o ID e a data de criação.
    Retorna uma lista de tuplas (container_id, created_at).
    """

    subprocess.run(
        ["podman", "machine", "start"],
        capture_output=True,
        text=True,
    )

    # Usa delimitador claro entre os campos para evitar problemas com espaços
    result = subprocess.run(
        ["podman", "ps", "-a", "--format", "{{.ID}}||{{.CreatedAt}}||{{.Names}}"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        wr.wLog("Erro ao listar contêineres")
        return []
    
    wr.wLog(f"Saída podman:\n{result.stdout}")
    
    containers = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("||")
        if len(parts) == 3:
            container_id, created_at, name = [p.strip() for p in parts]
            if name.startswith("osmr_"):
                containers.append((container_id, created_at))

    return containers

################################################################################
def get_container_by_cacheid(cacheid):
    """
    Retorna uma lista com o contêiner cujo nome começa com 'osmr_' e contém o cacheid.
    Para cada contêiner, inclui: (container_id, created_at, porta)
    """

    result = subprocess.run(
        ["podman", "ps", "-a", "--format", "{{.ID}}||{{.CreatedAt}}||{{.Names}}"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        wr.wLog("Erro ao listar contêineres")
        return []

    containers = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("||")
        if len(parts) == 3:
            container_id, created_at, name = [p.strip() for p in parts]
            if name.startswith("osmr_") and cacheid in name:
                # Obtemos a(s) porta(s)
                port_result = subprocess.run(
                    ["podman", "port", container_id],
                    capture_output=True,
                    text=True,
                )
                if port_result.returncode == 0:
                    porta = port_result.stdout.strip().splitlines()[0] if port_result.stdout.strip() else "desconhecida"
                else:
                    porta = "erro"
                containers.append((container_id, created_at, porta))

    return containers
###########################################################################################################################
def start_or_find_server_for_this_route(start_lat, start_lon, end_lat, end_lon): 
    # cache =  cb.cCacheBoundingBox.find_server_for_this_route(start_lat, start_lon, end_lat, end_lon)
    # resultados = get_container_by_cacheid(cache)
    # for cid, created, porta in resultados:
    #    print(f"ID: {cid}, Criado: {created}, Porta: {porta}")    
    return
################################################################################

def load_config_numcontainers():
    """
    Carrega o número máximo de contêineres permitidos em execução a partir do arquivo JSON.
    Retorna 5 se não conseguir carregar.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return int(config.get("numcontainersmax", 5))
    except Exception as e:
        wr.wLog(f"Erro ao carregar {CONFIG_FILE}: {e}")
        return 4

################################################################################
def keep_last_n_containers_running():
    """
    Mantém apenas os contêineres mais recentes definidos no JSON em execução.
    """
    num_max = load_config_numcontainers()
    containers = get_containers()
    now = datetime.datetime.now()

    def parse_created_time(created_at):
        try:
            cleaned = " ".join(created_at.split()[:2])[:26]
            return datetime.datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return now  # Se falhar, assume como se fosse "agora"

    containers_sorted = sorted(
        containers, key=lambda c: parse_created_time(c[1]), reverse=True
    )

    ids_to_keep = {c[0] for c in containers_sorted[:num_max]}

    result = subprocess.run(
        ["podman", "ps", "--format", "{{.ID}}"],
        capture_output=True,
        text=True,
    )
    running_ids = set(result.stdout.strip().splitlines())

    for container_id in running_ids:
        if container_id not in ids_to_keep:
            wr.wLog(f"Parando conteiner: {container_id}")
            subprocess.run(
                ["podman", "stop", container_id],
                stdout=subprocess.DEVNULL
            )
            
################################################################################
def StopOldContainers(days=30):
    """
    Para contêineres que têm mais de 'days' dias de idade.
    """
    # Obtém a data atual
    current_time = datetime.datetime.now()

    # Obtém os contêineres
    containers = get_containers()

    for container_id, created_at in containers:
        # Converte a data de criação para um objeto datetime
        try:
            # Remover a parte extra do fuso horário (a última parte)
            created_at_cleaned = (
                created_at.split(" ")[0] + " " + created_at.split(" ")[1]
            )  # Remove a parte extra de fuso horário
            created_at_cleaned = created_at_cleaned[:26]
            # wLog("---------------------- Data com problema "+created_at_cleaned)
            created_time = datetime.datetime.strptime(
                created_at_cleaned, "%Y-%m-%d %H:%M:%S.%f"
            )
        except ValueError:
            # Caso o formato de data não tenha microsegundos
            created_at_cleaned = (
                created_at.split(" ")[0] + " " + created_at.split(" ")[1]
            )  # Remove a parte extra de fuso horário
            created_at_cleaned = created_at_cleaned[:26]
            # wLog("---------------------- Data ajustada "+created_at_cleaned)
            created_time = datetime.datetime.strptime(
                created_at_cleaned, "%Y-%m-%d %H:%M:%S.%f"
            )

        # Calcula a diferença de dias entre a data atual e a data de criação
        age_in_days = (current_time - created_time).days
        # wLog(f"---------------------- age_in_days: {age_in_days}")

        # Se o contêiner for mais antigo que o limite (30 dias)
        if age_in_days > days:
            wr.wLog(f"Parando contêiner {container_id} (idade: {age_in_days} dias)")
            subprocess.run(["podman", "stop", container_id])


################################################################################
def VerificarOsrmAtivo(tentativas=1000, intervalo=5):
    """
    Verifica se o servidor OSRM está ativo.

    Args:
    - url: URL do serviço de rota OSRM.
    - tentativas: Número máximo de tentativas de verificação.
    - intervalo: Intervalo de tempo (em segundos) entre as tentativas.

    Returns:
    - bool: True se o servidor estiver no ar, False caso contrário.
    """
    url = f"http://localhost:{wr.UserData.OSMRport}/route/v1/driving/-43.105772903105354,-22.90510838815471;-43.089637952126694,-22.917360518277434?overview=full&geometries=polyline&steps=true"

    for tentativa in range(tentativas):
        try:
            # Faz a requisição GET
            response = requests.get(url)

            # Verifica o código de status HTTP
            if response.status_code == 200:
                wr.wLog("OSRM está funcionando corretamente.", level="debug")
                return True
            else:
                wr.wLog(
                    f"Tentativa {tentativa + 1}/{tentativas}: Erro {response.status_code}. Tentando novamente...",
                    level="debug",
                )
                if VerificarFalhaServidorOSMR():
                    return False

        except requests.exceptions.RequestException as e:
            wr.wLog(
                f"Tentativa {tentativa + 1}/{tentativas}: Erro ao acessar o OSRM: {e}. Tentando novamente...",
                level="debug",
            )
            if VerificarFalhaServidorOSMR():
                return False

        # Aguarda o intervalo antes de tentar novamente
        time.sleep(intervalo)

    wr.wLog(
        "O servidor OSRM não ficou disponível após várias tentativas.", level="debug"
    )
    return False


################################################################################
def procurar_multiplas_strings_em_arquivo(caminho_arquivo, lista_strings):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                for s in lista_strings:
                    if s in linha:
                        return True
        return False
    except FileNotFoundError:
        wr.wLog(f"Arquivo não encontrado: {caminho_arquivo}")
        return False
    except Exception as e:
        wr.wLog(f"Erro ao ler o arquivo: {e}")
        return False


################################################################################
def VerificarFalhaServidorOSMR():
    erros_procurados = [
        "terminate called after throwing an instance of",
        "Required files are missing, cannot continue",
        "Error: CreateFile TempData",
        "Error: statfs",
        "Unable to restore terminal:",
    ]
    log_filename = wl.get_log_filename()
    logfile = f"{log_filename}.{wr.UserData.nome}.OSMR"
    if procurar_multiplas_strings_em_arquivo(logfile, erros_procurados):
        wr.wLog("Erro detectado no log!", level="debug")
        return True
    else:
        wr.wLog("Nenhum erro encontrado no log.", level="debug")
        return False


################################################################################
def KillProcessByCommand(target_command):
    """
    Encerra processos com base em um comando específico.

    :param target_command: Parte do comando que identifica o processo a ser encerrado (string).
    """
    found = False  # Para verificar se algum processo foi encontrado
    for process in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            # Obtém a linha de comando do processo
            cmdline = process.info["cmdline"]
            # Verifica se cmdline não é None e contém o comando alvo
            if cmdline and target_command in cmdline:
                wr.wLog(
                    f"Matando processo {process.info['name']} (PID: {process.info['pid']})"
                )
                process.kill()  # Encerra o processo
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if not found:
        # wLog(f"Nenhum processo encontrado com o comando '{target_command}'.")
        pass
    else:
        # wLog("Processo encerrado com sucesso, se encontrado.")
        pass


################################################################################
def MataServidorWebRotas():
    KillProcessByCommand("Server.py")
    return


################################################################################
def VerificaArquivosIguais(arquivo_atual, arquivo_backup):
    # Verifica se ambos os arquivos existem
    if not os.path.exists(arquivo_atual):
        wr.wLog(f"O arquivo atual '{arquivo_atual}' não existe.", level="warning")
        return False
    if not os.path.exists(arquivo_backup):
        wr.wLog(f"O arquivo backup '{arquivo_backup}' não existe.", level="warning")
        return False

    # Compara os arquivos
    arquivos_sao_iguais = filecmp.cmp(arquivo_atual, arquivo_backup, shallow=False)
    return arquivos_sao_iguais


###########################################################################################################################
def DeleteOldFilesAndFolders(directory, days=30):
    """
    Remove arquivos e pastas (inclusive não vazias) mais antigos que um número específico de dias.

    Args:
        directory (str): Caminho para o diretório base.
        days (int): Número de dias para considerar como o limite. Padrão é 30.

    DeleteOldFilesAndFolders("/caminho/para/seu/diretorio", days=30)
    """
    try:
        # Calcula a data limite
        now = time.time()
        cutoff = now - (days * 86400)  # 86400 segundos por dia

        # Itera pelos itens no diretório
        for filename in os.listdir(directory):
            item_path = os.path.join(directory, filename)

            # Obtém o tempo de modificação do item
            item_mtime = os.path.getmtime(item_path)

            # Verifica se é um arquivo
            if os.path.isfile(item_path) and item_mtime < cutoff:
                os.remove(item_path)
                wr.wLog(f"Arquivo removido: {item_path}")

            # Verifica se é um diretório
            elif os.path.isdir(item_path) and item_mtime < cutoff:
                # Remove o diretório e todo o seu conteúdo
                shutil.rmtree(item_path)  # Remove diretórios e seus conteúdos
                wr.wLog(f"Pasta removida: {item_path}")
    except Exception as e:
        wr.wLog(f"Erro ao processar o diretório: {e}")


################################################################################
def parar_containers_osmr(nome_usuario):
    try:
        # Lista os containers com nome
        podman_ps = subprocess.run(
            ["podman", "ps", "-a", "--format", "{{.ID}} {{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        linhas = podman_ps.stdout.strip().splitlines()
        for linha in linhas:
            container_id, container_name = linha.strip().split(maxsplit=1)
            # if container_name == f"osmr_{nome_usuario}":
            if container_name.startswith(f"osmr_{nome_usuario}_"):    
                subprocess.run(
                    ["podman", "stop", container_id],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                wr.wLog(f"Container {container_name} parado.", level="debug")

    except Exception as e:
        wr.wLog(f"Erro ao parar containers: {e}", level="debug")


################################################################################
def remover_arquivos_osmr():
    wr.wLog("Removendo arquivos osmozis e osmr", level="debug")

    caminhos = [f"../../resources/Osmosis/TempData/exclusion_{wr.UserData.nome}*"]

    for caminho in caminhos:
        for item in glob.glob(caminho, recursive=True):
            try:
                if os.path.isfile(item):
                    os.remove(item)
                    wr.wLog(f"Arquivo removido: {item}", level="debug")
                elif os.path.isdir(item):
                    shutil.rmtree(item)
                    wr.wLog(f"Diretório removido: {item}", level="debug")
            except Exception as e:
                wr.wLog(f"Erro ao remover {item}: {e}", level="error")


################################################################################
def esperar_container_parar(nome_usuario, timeout=30):
    for _ in range(timeout):
        # Verifica se o container ainda está rodando
        result = subprocess.run(
            ["podman", "ps", "--filter", f"name={nome_usuario}", "--format", "{{.ID}}"],
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            return  # Container finalizou
        time.sleep(1)
    raise TimeoutError(
        f"Container de {nome_usuario} ainda está ativo após {timeout} segundos."
    )


################################################################################
def limpar_cache_files_osmr(regioes):
    try:
        wr.wLog(
            f"Parando todos os containers osmr do usário {wr.UserData.nome}",
            level="debug",
        )
        parar_containers_osmr(wr.UserData.nome)
        esperar_container_parar(wr.UserData.nome)
        wr.wLog("Apagando arquivo de log...", level="debug")
        log_filename = wl.get_log_filename()
        log_file = f"{log_filename}.{wr.UserData.nome}.OSMR"
        backup_file = log_file + ".LastError"
        try:
            if os.path.exists(log_file):
                shutil.copy(log_file, backup_file)
                wr.wLog(f"Cópia de segurança criada: {backup_file}", level="debug")
            os.remove(log_file)
            wr.wLog(f"Removido: {log_file}", level="debug")
        except FileNotFoundError:
            wr.wLog(f"Arquivo não encontrado: {log_file}")
        except Exception as e:
            wr.wLog(f"Erro ao remover {log_file}: {e}")
        remover_arquivos_osmr()
        wr.wLog("Limpeza concluída com sucesso.", level="debug")
    except Exception as e:
        wr.wLog(f"Erro durante a limpeza dos caches : {e}")

    cb.cCacheBoundingBox.delete(regioes)


################################################################################
def PreparaServidorRoteamento(regioes):
    roteamento_ok = False
    gi.cGuiOutput.cache_id = cb.cCacheBoundingBox.chave(regioes)
    while not roteamento_ok:
        if cb.cCacheBoundingBox.get_cache(regioes) == None:
            wr.GeraArquivoExclusoes(
                regioes,
                arquivo_saida=Path(f"{pf.OSMOSIS_TEMPDATA_PATH}")
                / f"exclusion_{cb.cCacheBoundingBox.chave(regioes)}.poly",
            )
            cb.cCacheBoundingBox.route_cache_clear_regioes()
            wr.wLog("FiltrarRegiãoComOsmosis")
            if FiltrarRegiaoComOsmosis(regioes) == 1:
                wr.wLog("GerarIndicesExecutarOSRMServer")
                GerarIndicesExecutarOSRMServer(regioes)
            else:
                wr.wLog(
                    "Dados de roteamento encontrados no diretorio filtro OSMR cache, ativando o servidor OSMR"
                )
                AtivaServidorOSMR(regioes)
            info_regiao = sf.ObterMunicipiosNoBoundingBoxOrdenados(
                rg.extrair_bounding_box_de_regioes(regioes)
            )
            km2_região = wr.calc_km2_regiao(regioes)
            cb.cCacheBoundingBox.new(
                regioes,
                f"filtro_{cb.cCacheBoundingBox.chave(regioes)}",
                info_regiao,
                km2_região,
            )
        else:
            wr.wLog(
                "Dados de roteamento encontrados no cache, nao e necessario executar osmosis"
            )
            AtivaServidorOSMR(regioes)
        if VerificarOsrmAtivo():
            roteamento_ok = True
        else:
            cache_id = cb.cCacheBoundingBox.chave(regioes)
            wr.wLog(
                f"Erro de cache encontrado reiniciando geração dos mapas - id: {cache_id}"
            )
            limpar_cache_files_osmr(regioes)


################################################################################
