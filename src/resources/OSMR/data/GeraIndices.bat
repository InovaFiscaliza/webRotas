@echo off
rem Verifica se o parametro foi passado
if "%1"=="" goto Erro

set USER=%1
set LOG_SAIDA=%2
set DIRETORIO_REGIAO="TempData/filtro_%USER%"

rem podman commit 572b60c4b455  osmr_webrota
rem podman save -o osmr_webrota.tar osmr_webrota

rem Comandos preparatórios
podman machine init >> %LOG_SAIDA% 2>&1
podman machine start >> %LOG_SAIDA% 2>&1
podman stop osmr_%USER% >> %LOG_SAIDA% 2>&1
podman load -i osmr_webrota.tar >> %LOG_SAIDA% 2>&1
podman run --rm --name temp1%USER% -m 32g -t -v "%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osmr_webrota osrm-extract -p /opt/car.lua /data/%DIRETORIO_REGIAO%/filtro-latest.osm.pbf >> %LOG_SAIDA% 2>&1
podman run --rm --name temp2%USER% -m 32g -t -v "%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osmr_webrota osrm-partition /data/%DIRETORIO_REGIAO%/filtro-latest.osm.pbf >> %LOG_SAIDA% 2>&1
podman run --rm --name temp3%USER% -m 32g -t -v "%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osmr_webrota osrm-customize /data/%DIRETORIO_REGIAO%/filtro-latest.osm.pbf >> %LOG_SAIDA% 2>&1

exit /b
:Erro
    echo Erro: Nenhum usuario especificado
    echo Uso: script.bat <user>
    exit /b