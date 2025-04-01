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

import webRota as wr

server_port = 5001
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
def FiltrarRegiãoComOsmosis():
    # Salvar o diretório atual
    diretorio_atual = os.getcwd()
    os.chdir("../../resources/Osmosis")
    # Inicia e configura a máquina do Podman
    logok=f"{wr.log_filename}.{wr.UserData.nome}"
    subprocess.run(["filter.bat", wr.UserData.nome,logok])   # f"{log_filename}.{UserData.nome}"
    os.chdir(diretorio_atual)

################################################################################
def AtivaServidorOSMR():
    # startserver filtro 8001 osmr_server8001
    StopOldContainers(days=30)
    diretorio_atual = os.getcwd()
    os.chdir("../../resources/OSMR/data")
    wr.UserData.OSMRport = FindFreePort(start_port=50000, max_port=65535)
    wr.wLog(f"Porta tcp/ip disponivel en   contrada: {wr.UserData.OSMRport}",level="debug")
    logok=f"{wr.log_filename}.{wr.UserData.nome}"
    wr.wLog(f"Ativando Servidor OSMR",level="info")
    # Assegura que o container executa em paralelo com o python
    subprocess.Popen(["StartServer.bat", str(wr.UserData.OSMRport), wr.UserData.nome, logok], shell=True)
    os.chdir(diretorio_atual)
    return


################################################################################
def GerarIndicesExecutarOSRMServer():
    # Salvar o diretório atual
    diretorio_atual = os.getcwd()
    os.chdir("../../resources/OSMR/data")
    DeleteOldFilesAndFolders("TempData", days=30)
    logok=f"{wr.log_filename}.{wr.UserData.nome}"
    subprocess.run(["GeraIndices.bat", wr.UserData.nome,logok])
    os.chdir(diretorio_atual)
    AtivaServidorOSMR()
    return


################################################################################
def get_containers():
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
                wr.wLog("OSRM está funcionando corretamente.")
                return True
            else:
                wr.wLog(
                    f"Tentativa {tentativa + 1}/{tentativas}: Erro {response.status_code}. Tentando novamente...",level="debug"
                )

        except requests.exceptions.RequestException as e:
            wr.wLog(
                f"Tentativa {tentativa + 1}/{tentativas}: Erro ao acessar o OSRM: {e}. Tentando novamente...",level="debug"
            )

        # Aguarda o intervalo antes de tentar novamente
        time.sleep(intervalo)

    wr.wLog("O servidor OSRM não ficou disponível após várias tentativas.",level="debug")
    return False


################################################################################
def AtivaServidorWebRotas():
    teste = wr.VerificarServidorAtivo(
        f"http://localhost:{server_port}/ok", "ok", tentativas=3, intervalo=1
    )
    if not teste:
        if wr.log_filename == "":
            subprocess.Popen(
                ["start", "startserver.bat"],
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            wr.wLog("Ativando Servidor")
            return
        else:
            wr.wLog(f"Ativando Servidor log {wr.log_filename}")
            with open(wr.log_filename, "w+", encoding="utf-8") as log_file:
                subprocess.Popen(
                    ["startserver.bat"],
                    stdout=log_file,
                    stderr=log_file,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            return
    else:
        wr.wLog("Servidor Ativo")
    return


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
        wr.wLog(f"O arquivo atual '{arquivo_atual}' não existe.",level="warning")
        return False
    if not os.path.exists(arquivo_backup):
        wr.wLog(f"O arquivo backup '{arquivo_backup}' não existe.",level="warning")
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
def PreparaServidorRoteamento(regioes):
    DeleteOldFilesAndFolders("logs", days=30)
    DeleteOldFilesAndFolders("../../resources/Osmosis/TempData", days=30)
    wr.GeraArquivoExclusoes(
        regioes,
        arquivo_saida=f"../../resources/Osmosis/TempData/exclusion_{wr.UserData.nome}.poly",
    )
    if not VerificaArquivosIguais(
        f"../../resources/Osmosis/TempData/exclusion_{wr.UserData.nome}.poly",
        f"../../resources/Osmosis/TempData/exclusion_{wr.UserData.nome}.poly.old",
    ):
        wr.wLog("FiltrarRegiãoComOsmosis")
        FiltrarRegiãoComOsmosis()
        wr.wLog("GerarIndicesExecutarOSRMServer")
        GerarIndicesExecutarOSRMServer()
    else:
        wr.wLog("Arquivo exclusoes nao modificado, nao e necessario executar osmosis")
        AtivaServidorOSMR()
    VerificarOsrmAtivo()



################################################################################
