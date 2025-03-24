

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
# Verifica se está conectado na VPN da Anatel
if (Testar-Conexao -nomehost "sistemasnet") {
    Write-Host "Acesso a rede Anatel verificado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Nao foi possivel acessar a rede. Conecte-se a VPN da Anatel." -ForegroundColor Red
    exit 0
}
Invoke-WebRequest -OutFile resources.zip -Uri $urlResources
# Test-DownloadedFile -outputFile "resources.zip"
Expand-Archive -LiteralPath resources.zip -DestinationPath .\
rm resources.zip
# ----------------------------------------------------------------------------------------------------------------------
