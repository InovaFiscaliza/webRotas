     Este é o container original que foi salvo com os comandos
     podman run -p 9966:9966 osrm/osrm-frontend
     podman commit 572b60c4b455  osrm_webrota
     podman save -o osrm_webrota.tar osrm_webrota


Baixar dados do Brasil
    https://download.geofabrik.de/south-america/brazil.html 
    wsl wget https://download.geofabrik.de/south-america/brazil-latest.osm.pbf

https://hub.docker.com/r/osrm/osrm-backend/


Comandos preparatórios

    docker run -t -v "C:\Users\andre\Documents\NetBeansProjects\missoes2023\Missoes2023\Missoes2024\GrupoInovaFiscaliza\webrotas\OSMR\data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/sudeste-latest.osm.pbf
    docker run -t -v "C:\Users\andre\Documents\NetBeansProjects\missoes2023\Missoes2023\Missoes2024\GrupoInovaFiscaliza\webrotas\OSMR\data:/data" osrm/osrm-backend osrm-partition /data/sudeste-latest.osrm
    docker run -t -v "C:\Users\andre\Documents\NetBeansProjects\missoes2023\Missoes2023\Missoes2024\GrupoInovaFiscaliza\webrotas\OSMR\data:/data" osrm/osrm-backend osrm-customize /data/sudeste-latest.osrm

Rodar servidor (só precisa deixar esse o resto pode apagar, só são usados na preparação)

    docker run -t -i -p 5000:5000 -v "C:\Users\andre\Documents\NetBeansProjects\missoes2023\Missoes2023\Missoes2024\GrupoInovaFiscaliza\webrotas\OSMR\data:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/sudeste-latest.osrm


Testar
    http://127.0.0.1:5000/route/v1/driving/13.388860,52.517037;13.385983,52.496891?steps=true
    http://127.0.0.1:5000/route/v1/driving/-22.880679892952166,-43.23110502630755;-22.899298036544902,-43.22175013960713?steps=true


Optionally start a user-friendly frontend on port 9966, and open it up in your browser
    
     Este é o container original que foi salvo com os comandos
     docker run -p 9966:9966 osrm/osrm-frontend
     podman commit 572b60c4b455  osrm_webrota
     podman save -o osrm_webrota.tar osrm_webrota
     
     docker run -p 9966:9966 osrm/osrm-frontend
    
     docker run -t -i -p 9966:9966 -v "C:\Users\andre\Documents\NetBeansProjects\missoes2023\Missoes2023\Missoes2024\GrupoInovaFiscaliza\webrotas\OSMR\data:/data" osrm/osrm-frontend osrm-routed --algorithm mld /data/sudeste-latest.osrm

##########################################################################
Carregar rota no google maps (arquivo gpx)

      https://donrox.com/en/blogs/post-1/import-gpx-google-maps