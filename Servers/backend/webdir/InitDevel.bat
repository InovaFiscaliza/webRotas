call C:\Users\andre\miniconda3\condabin\conda.bat activate webrotas
title Webdir

start cmd /k "docker run -t -i -p 5000:5000 -v "C:\Users\andre\Documents\NetBeansProjects\missoes2023\Missoes2023\Missoes2024\GrupoInovaFiscaliza\webrotas\OSMR\data:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/sudeste-latest.osrm"
start cmd /k "python Server.py"
start cmd /k "python Test.py"
