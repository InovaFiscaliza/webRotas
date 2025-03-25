taskkill /F /IM python.exe /T
FOR /F "tokens=*" %%i IN ('podman ps -a -q') DO podman stop %%i
wsl rm -rf logs/Web*
wsl rm -rf ../../resources/Osmosis/TempData/exclu*
wsl rm -rf ../../resources/OSMR/data/TempData/filtro*
wsl rm -rf templates/WebRotas*