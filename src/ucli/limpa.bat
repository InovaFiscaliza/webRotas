taskkill /F /IM python.exe /T
FOR /F "tokens=*" %%i IN ('podman ps -a -q') DO podman stop %%i
wsl rm -rf "%WEBROTAS_HOME%\src\backend\webdir\logs\Web*"
wsl rm -rf "%WEBROTAS_HOME%\src\resources\Osmosis\TempData\exclu*"
wsl rm -rf "%WEBROTAS_HOME%\src\resources\OSMR\data\TempData\filtro_*"
wsl rm -rf "%WEBROTAS_HOME%\src\backend\webdir\templates\Mapa*"