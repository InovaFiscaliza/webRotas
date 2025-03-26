<#
.SYNOPSIS
Pack essential application files to create release package.

.DESCRIPTION
This script is used to pack essential application files to create a release package.
#>

# --------------------------------------------------------------------------
# Diretório de destino do pacote
$destinationRoot = "webRotas"
# Lista de pastas a serem criadas dentro do diretório de destino
$folders = @(
    "src\backend\webdir\logs",
    "src\backend\webdir\static",
    "src\backend\webdir\TempData",
    "src\backend\webdir\templates",
    "src\resources\BR_Municipios",
    "src\resources\Comunidades",
    "src\resources\Urbanizacao",
    "src\resources\Osmosis\brazil",
    "src\resources\Osmosis\TempData",
    "src\resources\OSMR\data",
    "src\resources\OSMR\data\TempData",
    "src\ucli",
    "tests"
)

# Lista de arquivos a serem copiados
$files = @(
    "pyproject.toml",
    "uv.lock",
    "src\backend\webdir\geraMapa.py",
    "src\backend\webdir\limpaTodosArquivosTemporarios.bat",
    "src\backend\webdir\port_test.py",
    "src\backend\webdir\server.py",
    "src\backend\webdir\server_env.py",
    "src\backend\webdir\shapeFiles.py",
    "src\backend\webdir\uf_code.py",
    "src\backend\webdir\webRota.py",
    "src\backend\webdir\static\clDivOrdenaPontos.js",
    "src\backend\webdir\static\GpsAtivo.png",
    "src\backend\webdir\static\GpsInativo.png",
    "src\backend\webdir\static\iconcar.png",
    "src\backend\webdir\static\Kml.png",
    "src\backend\webdir\static\MapLayers.png",
    "src\backend\webdir\static\mapcontextmenu.js",
    "src\backend\webdir\static\OpenElevTable.png",
    "src\backend\webdir\static\OrdemPontos.png",
    "src\backend\webdir\static\Pointer.png",
    "src\backend\webdir\static\PointerNorte.png",
    "src\backend\webdir\static\RedPin.png",
    "src\backend\webdir\static\StaticResources.js",
    "src\backend\webdir\static\tmpStaticResources.js",
    "src\backend\webdir\static\UtilMap.js",
    "src\resources\Osmosis\filter.bat",
    "src\resources\OSMR\data\GeraIndices.bat",
    "src\resources\OSMR\data\StartServer.bat",
    "src\ucli\demo_payload.json",
    "src\ucli\json_validate.py",
    "src\ucli\server_interface.py",
    "src\ucli\webrotas.bat",
    "src\ucli\webrota_client.py",
    "src\ucli\prompt_conf.bat",
    "src\ucli\limpa.bat",
    "src\ucli\mensagens.txt",
    "src\ucli\webrotas.lnk",
    "tests\exemplo_abrangencia_rj_campos.json",
    "tests\exemplo_abrangencia_rj_niteroi_geodesica.json",
    "tests\exemplo_abrangencia_sp_pesado.json",
    "tests\exemplo_contorno.json",
    "tests\exemplo_visita_rj.json",
    "tests\exemplo_visita_ro.json",
    "tests\exemplo_visita_serra_rj.json"
)

# --------------------------------------------------------------------------
# Garante que estamos no diretório correto, desce um diretório
Set-Location $PSScriptRoot\..
# Garante que o .tmp está limpo
Remove-Item -Path "$destinationRoot" -Recurse -Force

# Cria o diretório de destino, se não existir
if (!(Test-Path $destinationRoot)) {
    mkdir $destinationRoot -Force
}

# Cria a estrutura de pastas dentro do diretório de destino
foreach ($folder in $folders) {
    $fullPath = Join-Path -Path $destinationRoot -ChildPath $folder
    if (!(Test-Path $fullPath)) {
        mkdir $fullPath -Force
    }
}

# Copia os arquivos para o destino correto
foreach ($file in $files) {
    $sourcePath = $file
    $destinationPath = Join-Path -Path $destinationRoot -ChildPath $file

    # Garante que a pasta de destino existe antes de copiar
    $destinationDir = Split-Path -Path $destinationPath -Parent
    if (!(Test-Path $destinationDir)) {
        mkdir $destinationDir -Force
    }

    # Copia apenas se o arquivo existir
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $destinationPath -Force
    } else {
        Write-Warning "File not found: $sourcePath"
    }
}
Remove-Item -Path webRotas.tgz -Recurse -Force
tar -cvzf webRotas.tgz $destinationRoot
Remove-Item -Path "$destinationRoot" -Recurse -Force

