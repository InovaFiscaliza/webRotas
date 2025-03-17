@echo off
rem Script para filtrar o arquivo .osm.pbf de acordo com o arquivo .poly
rem .
rem Comandos iniciais para salvar o osmosis_webrota.tar
rem podman run --rm -v .:/data yagajs/osmosis osmosis --read-pbf file="/data/brazil/brazil-latest.osm.pbf" --bounding-polygon file="/data/exclusion.poly" completeWays=no --write-pbf file="/data/filtro/filtro-latest.osm.pbf"
rem podman commit d7e1629f274f  osmosis_webrota
rem podman save -o osmosis_webrota.tar osmosis_webrota
rem podman load -i osmosis_webrota.tar
rem https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
rem siga esse tutorial de formato de arquivo e só esse cria a soluçao

if "%1"=="" goto Erro


set USER=%1
set FILTRO=TempData/filtro_%USER%

echo %date% %time% : Preparing Podman machine...
podman machine init
podman machine start
podman load -i osmosis_webrota.tar
wsl rm -rf %FILTRO%
wsl mkdir -p %FILTRO%

echo %date% %time% : Running osmosis container...
podman run --rm -v .:/data --name osmosis_%USER% localhost/osmosis_webrota osmosis --read-pbf file="/data/brazil/brazil-latest.osm.pbf" --bounding-polygon file="/data/TempData/exclusion_%USER%.poly" completeWays=no --write-pbf file="/data/%FILTRO%/filtro-latest.osm.pbf"
wsl rm -rf ../OSMR/data/%FILTRO%
wsl mkdir -p ../OSMR/data/%FILTRO%
wsl mv %FILTRO%/filtro-latest.osm.pbf ../OSMR/data/%FILTRO%/
wsl rm -rf %FILTRO%

exit /b
:Erro
    echo Erro:
    echo Uso: script.bat <user> 
    exit /b