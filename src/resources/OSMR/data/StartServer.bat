@echo off
rem Verifica se o parametro foi passado
if "%1"=="" goto Erro
if "%2"=="" goto Erro


set PORTA=%1
set USER=%2
set LOG_SAIDA=%3.OSMR
set DIRETORIO_REGIAO="TempData/filtro_%USER%"

rem Rodar servidor
podman machine init >> %LOG_SAIDA% 2>&1
podman machine start >> %LOG_SAIDA% 2>&1

podman stop osmr_%USER% >> %LOG_SAIDA% 2>&1
podman load -i osmr_webrota.tar >> %LOG_SAIDA% 2>&1

rem start podman run --rm --name osm_servidor -m 32g -t -i -p 5000:5000 -v ".\%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osrm_webrota osrm-routed --algorithm mld /data/%DIRETORIO_REGIAO%/%DIRETORIO_REGIAO%-latest.osrm
podman run --rm --name osmr_%USER% -m 32g -t -i -p %PORTA%:5000 -v ".\TempData\filtro_%USER%:/data/%DIRETORIO_REGIAO%" localhost/osmr_webrota  osrm-routed --algorithm mld /data/%DIRETORIO_REGIAO%/filtro-latest.osm.pbf >> %LOG_SAIDA% 2>&1

exit /b
:Erro
    echo Erro: Nenhuma regiao especificada.
    echo Uso: script.bat <porta> <usuario>
    exit /b