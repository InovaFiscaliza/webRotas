taskkill /F /IM python.exe /T
FOR /F "tokens=*" %%i IN ('podman ps -a -q') DO podman stop %%i
wsl rm -rf logs/*
wsl rm -rf ../../Osmosis/TempData/*
rmdir /s /q "..\..\OSMR\data\TempData"
mkdir "..\..\OSMR\data\TempData"
wsl rm -rf templates/Mapa*