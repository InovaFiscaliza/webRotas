taskkill /F /IM python.exe /T
FOR /F "tokens=*" %%i IN ('podman ps -a -q') DO podman stop %%i
rm -rf "%WEBROTAS_HOME%\src\backend\webdir\logs\Web*"
rm -rf "%WEBROTAS_HOME%\src\resources\Osmosis\TempData\exclu*"
rm -rf "%WEBROTAS_HOME%\src\resources\OSMR\data\TempData\filtro_*"
rm -rf "%WEBROTAS_HOME%\src\backend\webdir\templates\Mapa*"