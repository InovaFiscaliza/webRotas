<#
.SYNOPSIS
Pack essential application files to create release package.

.DESCRIPTION
This script is used to pack essential application files to create a release package.

#>

# --------------------------------------------------------------------------
# list of folders to be created (only end leafs)
$folders = @(
    "..\src\backend\webdir\logs",
    "..\src\backend\webdir\static",
    "..\src\backend\webdir\TempData",
    "..\src\backend\webdir\templates",
    "..\src\resources\BR_Municipios",
    "..\src\resources\Comunidades",
    "..\src\resources\Urbanizacao",
    "..\src\resources\Osmosis\brazil",
    "..\src\resources\Osmosis\TempData",
    "..\src\resources\OSMR\data",
    "..\src\resources\OSMR\data\TempData",
    "..\src\ucli",
    "..\tests"
)

# list of files to be copied
$files = @(
    "..\pyproject.toml",
    "..\uv.lock",
    "..\src\backend\webdir\geraMapa.py",
    "..\src\backend\webdir\limpaTodosArquivosTemporarios.bat",
    "..\src\backend\webdir\port_test.py",
    "..\src\backend\webdir\server.py",
    "..\src\backend\webdir\server_env.py",
    "..\src\backend\webdir\shapeFiles.py",
    "..\src\backend\webdir\TempData",
    "..\src\backend\webdir\templates",
    "..\src\backend\webdir\uf_code.py",
    "..\src\backend\webdir\webRota.py",
    "..\src\backend\webdir\static\clDivOrdenaPontos.js",
    "..\src\backend\webdir\static\GpsAtivo.png",
    "..\src\backend\webdir\static\GpsInativo.png",
    "..\src\backend\webdir\static\iconcar.png",
    "..\src\backend\webdir\static\Kml.png",
    "..\src\backend\webdir\static\mapcontextmenu.js",
    "..\src\backend\webdir\static\OpenElevTable.png",
    "..\src\backend\webdir\static\OrdemPontos.png",
    "..\src\backend\webdir\static\Pointer.png",
    "..\src\backend\webdir\static\PointerNorte.png",
    "..\src\backend\webdir\static\RedPin.png",
    "..\src\backend\webdir\static\StaticResources.js",
    "..\src\backend\webdir\static\tmpStaticResources.js",
    "..\src\backend\webdir\static\UtilMap.js",
    "..\src\resources\Osmosis\filter.bat",
    "..\src\resources\OSMR\data\GeraIndices.bat",
    "..\src\resources\OSMR\data\StartServer.bat",
    "..\src\ucli\demo_payload.json",
    "..\src\ucli\json_validate.py",
    "..\src\ucli\server_interface.py",
    "..\src\ucli\webrotas.bat",
    "..\src\ucli\webrota_client.py",
    "..\tests\exemplo_abrangencia_rj_campos.json",
    "..\tests\exemplo_abrangencia_rj_niteroi_geodesica.json",
    "..\tests\exemplo_abrangencia_sp_pesado.json",
    "..\tests\exemplo_contorno.json",
    "..\tests\exemplo_visita_rj.json",
    "..\tests\exemplo_visita_ro.json",
    "..\tests\exemplo_visita_serra_rj.json"
)

# --------------------------------------------------------------------------
# set working directory
Set-Location $PSScriptRoot/..
mkdir .tmp
Set-Location .tmp

for ($i = 0; $i -lt $folders.Length; $i++) {
    mkdir $folders[$i] -Force
}

# copy files
foreach ($file in $files) {
    Copy-Item -Path $file -Destination $file -Force
}