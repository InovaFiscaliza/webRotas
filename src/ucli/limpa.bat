taskkill /F /IM python.exe /T
FOR /F "tokens=*" %%i IN ('podman ps -a -q') DO podman stop %%i
wsl rm -rf C:\ProgramData\Anatel\webRotas\src\backend\webdir\logs\Web*
wsl rm -rf C:\ProgramData\Anatel\webRotas\src\resources\Osmosis\TempData\exclu*
wsl rm -rf C:\ProgramData\Anatel\webRotas\src\resources\OSMR\data\TempData\filtro_*
wsl rm -rf C:\ProgramData\Anatel\webRotas\src\backend\webdir\templates\Mapa*