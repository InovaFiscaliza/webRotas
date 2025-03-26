

# ----------------------------------------------------------------------------------------------------------------------
# URL do recurso no SharePoint
$urlResources = "https://anatel365.sharepoint.com/:u:/r/sites/InovaFiscaliza/DataHub%20%20GET/webRotas/resources.zip?csf=1&web=1&e=7fLElJ"
# ----------------------------------------------------------------------------------------------------------------------
function Testar-Conexao {
    param (
        [string]$nomehost
    )

    # Testa a conexão com o host
    $conexao = Test-Connection -ComputerName $nomehost -Count 1 -Quiet
    
    # Verifica se a conexão foi bem-sucedida
    if ($conexao) {
        return $true  # Conexão bem-sucedida
    } else {
        Write-Host "Erro ao tentar conectar ao host '$nomehost'" -ForegroundColor Red
        return $false  # Falhou a conexão
    }
}
# ----------------------------------------------------------------------------------------------------------------------
# Garante que estamos no diretório correto, desce um diretório
Set-Location $PSScriptRoot\..
# Verifica se está conectado na VPN da Anatel e resources.zip não existe
if (-not (Test-Path "resources.zip"))
{
    if (Testar-Conexao -nomehost "sistemasnet") {
        Write-Host "Acesso a rede Anatel verificado com sucesso!" -ForegroundColor Green
        Write-Host "Faça o download do arquivo resources.zip do link abaixo e o deixe na raiz do diretório webRotas." -ForegroundColor Green
        Write-Host $urlResources -ForegroundColor Green
        
    } else {
        Write-Host "Nao foi possivel acessar a rede. Conecte-se a VPN da Anatel." -ForegroundColor Red
        exit 0
    }
}
if (Test-Path "resources.zip") {
    Copy-Item -Path "resources.zip" -Destination "src\" -Force
    Set-Location -Path "src"
    Expand-Archive -LiteralPath "resources.zip" -DestinationPath ".\" -Force
} else {
    Write-Host "O arquivo resources.zip não foi encontrado."
    Write-Host "Faça o download do arquivo resources.zip do link abaixo e o deixe na raiz do diretório webRotas." -ForegroundColor Green
    Write-Host $urlResources -ForegroundColor Green    
    exit 0
}


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Obtém a versão do sistema operacional
# Define uma variável global para o tempo de espera
$Global:TempoEspera = 10
$osVersion = [System.Environment]::OSVersion.Version

# Exibe a versão completa
Write-Host "Detected Windows version: $osVersion"

# Extrai a versão principal (antes do ponto)
$majorVersion = $osVersion.Major

# Exibe a versão principal
Write-Host "Major version: $majorVersion"
# Verifica se a versão é maior ou igual a 10
if ($majorVersion -ge 10) {
    Write-Host "Your Windows version is 10 or greater. Proceeding with the script..."      
} else {
    Write-Host "Your Windows version is older than 10. Exiting..."
    exit
}
# ----------------------------------------------------------------------------------------------------------------------
# Verifica se o winget está instalado
$wingetExists = Get-Command winget -ErrorAction SilentlyContinue
if ($wingetExists) {
    Write-Host "Winget is installed. Proceeding with the script..."
} else {
    Write-Host "Winget is not installed. Exiting..." -ForegroundColor Red
    exit
}
# ----------------------------------------------------------------------------------------------------------------------
# Verifica se o Git está instalado
$gitExists = Get-Command git -ErrorAction SilentlyContinue

if ($gitExists) {
    Write-Host "Git is already installed. Version: $(git --version)"
} else {
    Write-Host "Git is not installed. Attempting to install it using winget..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget
    # Verifica se a instalação foi bem-sucedida
    $gitExists = Get-Command git -ErrorAction SilentlyContinue
    if ($gitExists) {
        Write-Host "Git has been successfully installed. Version: $(git --version)" -ForegroundColor Green
    } else {
        Write-Host "Git installation failed. Please install it manually." -ForegroundColor Red
        exit 1
    }
}
# ----------------------------------------------------------------------------------------------------------------------
# Verifica se o WSL está instalado
$wslVersion = wsl.exe --version 2>$null
if ($?) {
    Write-Host "WSL is already installed. Version details:" -ForegroundColor Green
    Write-Host $wslVersion
} else {
    Write-Host "WSL is not installed. Attempting to install it..." -ForegroundColor Yellow
    
    # Executa o comando de instalação do WSL
    wsl.exe --install

    # Aguarda um momento para a instalação ser concluída
    Start-Sleep -Seconds $Global:TempoEspera 

    # Verifica novamente se o WSL foi instalado corretamente
    $wslVersion = wsl.exe --version 2>$null
    if ($?) {
        Write-Host "WSL was successfully installed! Version details:" -ForegroundColor Green
        Write-Host $wslVersion
    } else {
        Write-Host "WSL installation failed. Please try installing manually." -ForegroundColor Red
        Write-Host "     wsl.exe --install" -ForegroundColor Red
        exit 1
    }
}
# ----------------------------------------------------------------------------------------------------------------------
# Verifica se o Podman está instalado
if (Get-Command podman -ErrorAction SilentlyContinue) {
    Write-Host "Podman já está instalado. Versão:" -ForegroundColor Green
    podman --version
} else {
    Write-Host "Podman não está instalado. Instalando agora..." -ForegroundColor Yellow

    # Instala o Podman usando winget
    winget install --id RedHat.Podman -e --source winget

    # Aguarda um momento para a instalação ser concluída
    Start-Sleep -Seconds $Global:TempoEspera 

    # Verifica novamente se o Podman foi instalado corretamente
    if (Get-Command podman -ErrorAction SilentlyContinue) {
        Write-Host "Podman foi instalado com sucesso! Versão:" -ForegroundColor Green
        podman --version
    } else {
        Write-Host "A instalação do Podman falhou. Tente instalar manualmente." -ForegroundColor Red
        Write-Host "    winget install --id RedHat.Podman -e --source winget" -ForegroundColor Red
        exit 1
    }
}
# ----------------------------------------------------------------------------------------------------------------------
# Verifica se o UV já está instalado
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "UV já está instalado. Versão:" -ForegroundColor Green
    uv --version
} else {
    Write-Host "UV não está instalado. Instalando agora..." -ForegroundColor Yellow

    # Instala o UV usando winget
    winget install --id=astral-sh.uv -e

    # Aguarda o tempo definido na variável global
    Start-Sleep -Seconds $Global:TempoEspera

    # Verifica novamente se o UV foi instalado corretamente
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host "UV foi instalado com sucesso! Versão:" -ForegroundColor Green
        uv --version
    } else {
        Write-Host "A instalação do UV falhou. Tente instalar manualmente." -ForegroundColor Red
        Write-Host "    winget install --id=astral-sh.uv -e" -ForegroundColor Red
        exit 1
    }
}
# ----------------------------------------------------------------------------------------------------------------------
# Verifica se `uv init` já foi executado verificando o arquivo `pyproject.toml`
if (Test-Path "pyproject.toml") {
    Write-Host "O projeto já foi inicializado com UV (pyproject.toml encontrado)." -ForegroundColor Cyan
} else {
    Write-Host "Inicializando o projeto com UV..." -ForegroundColor Yellow
    uv init

    # Verifica se o `uv init` foi bem-sucedido
    if (Test-Path "pyproject.toml") {
        Write-Host "UV init concluído com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Falha ao inicializar UV. Verifique manualmente." -ForegroundColor Red
        exit 1
    }
}
# ----------------------------------------------------------------------------------------------------------------------
# Executa o comando uv sync e captura a saída
$process = Start-Process -FilePath "uv" -ArgumentList "sync" -NoNewWindow -PassThru -Wait
# Verifica se a execução foi bem-sucedida
if ($process.ExitCode -eq 0) {
    Write-Host "O comando 'uv sync' foi executado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Erro ao executar 'uv sync'. Código de saída: $($process.ExitCode)" -ForegroundColor Red
    exit 1  # Encerra o script com erro
}
# ----------------------------------------------------------------------------------------------------------------------
Write-Host "webRotas configurado com sucesso!" -ForegroundColor Green
