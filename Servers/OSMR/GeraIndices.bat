@echo off
rem Verifica se o parametro foi passado
if "%1"=="" goto erro

set DIRETORIO_REGIAO=%1


rem podman commit 572b60c4b455  osrm_webrota
rem podman save -o osrm_webrota.tar osrm_webrota

rem Comandos preparatórios
podman machine init
podman machine start
podman stop osm_servidor 
podman load -i osrm_webrota.tar
podman run --rm --name temp1 -m 32g -t -v ".\%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osrm_webrota osrm-extract -p /opt/car.lua /data/%DIRETORIO_REGIAO%/%DIRETORIO_REGIAO%-latest.osm.pbf
podman run --rm --name temp2 -m 32g -t -v ".\%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osrm_webrota osrm-partition /data/%DIRETORIO_REGIAO%/%DIRETORIO_REGIAO%-latest.osrm
podman run --rm --name temp3 -m 32g -t -v ".\%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osrm_webrota osrm-customize /data/%DIRETORIO_REGIAO%/%DIRETORIO_REGIAO%-latest.osrm

rem Rodar servidor

podman run --rm --name osm_servidor -m 32g -t -i -p 5000:5000 -v ".\%DIRETORIO_REGIAO%:/data/%DIRETORIO_REGIAO%" localhost/osrm_webrota osrm-routed --algorithm mld /data/%DIRETORIO_REGIAO%/%DIRETORIO_REGIAO%-latest.osrm
exit /b
:Erro
    echo Erro: Nenhuma regiao especificada.
    echo Uso: script.bat <nome_da_regiao>
    exit /b