taskkill /F /IM python.exe /T
FOR /F "tokens=*" %%i IN ('podman ps -a -q') DO podman stop %%i
del /Q /S "%WEBROTAS_HOME%\src\backend\webdir\logs\Web*"
del /Q /S "%WEBROTAS_HOME%\src\resources\Osmosis\TempData\exclu*"
del /Q /S "%WEBROTAS_HOME%\src\backend\webdir\templates\WebRotas*"