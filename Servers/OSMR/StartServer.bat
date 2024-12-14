@echo off
rem Verifica se o parametro foi passado
if "%1"=="" goto Erro

set DIRETORIO_REGIAO=%1


rem Rodar servidor
rem podman machine init
rem podman machine start

rem podman stop osm_servidor
rem podman rm osm_servidor
podman run --name osm_servidor -m 32g -t -i -p 5000:5000 -v "\data\%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" osrm/osrm-backend osrm-routed --algorithm mld /data/%DIRETORIO_REGIAO%/%DIRETORIO_REGIAO%-latest.osrm
exit /b
:Erro
    echo Erro: Nenhuma regiao especificada.
    echo Uso: script.bat <nome_da_regiao>
    exit /b