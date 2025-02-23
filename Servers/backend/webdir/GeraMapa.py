import WebRota as wr
import os
###########################################################################################################################
def GeraHeader():
    header = """
        <!DOCTYPE html>
        <html lang="pt">
        <head>
            <base target="_top">
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            
            <title>Web Rotas</title>
            
            <link rel="shortcut icon" type="image/x-icon" href="docs/images/favicon.ico" />
                <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    
        <script>
            L_NO_TOUCH = false;
            L_DISABLE_3D = false;
        </script>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

            <style>
                html, body { width: 100%;height: 100%;margin: 0;padding: 0;
                }
            </style>
        </head>
        <body>

        <div id="map" style="width: 100vw; height: 100vh;"></div>
        <div id="gpsInfo" style="font-family: Arial, sans-serif; font-size: 16px; z-index: 1000; position: absolute; 
                                top: 10px; left: 50px;    background-color: white;"></div>
                  

        <script>
            
        """
    return header
###########################################################################################################################
def GeraFooter():
    footer = """
           </script>
        </body>
        </html>
    """        
    return footer
###########################################################################################################################
def AbrirArquivoComoString(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()  # Lê todo o conteúdo do arquivo como uma string
    except FileNotFoundError:
        return f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado."
    except Exception as e:
        return f"Erro: {e}"
###########################################################################################################################    
def WriteToFile(file_path, content):
    """
    Escreve uma string em um arquivo, sobrescrevendo o conteúdo existente.

    :param file_path: Caminho do arquivo onde a string será escrita.
    :param content: String a ser escrita no arquivo.
    """
    try:
        with open(file_path, 'a') as file:  # Modo 'w' para sobrescrever o arquivo
            file.write(content)
        print(f"Conteúdo gravado com sucesso no arquivo: {file_path}")
    except Exception as e:
        print(f"Erro ao gravar no arquivo: {e}")
###########################################################################################################################    
def GeraElevationTable():
    wr.wLog(f"GeraElevationTable")
    nomeuser=wr.UserData.nome
    fileElevation = f'static/elevation_table{nomeuser}.png'
    wr.generate_elevation_table_png(output_filename=fileElevation,min_elevation=wr.MinAltitude,max_elevation=wr.MaxAltitude)     
    base64ElevationTable = wr.FileToDataUrlBase64(fileElevation)
    if os.path.exists(fileElevation):
       os.remove(fileElevation)
    content = f"imgElevationTable = 'url(\"{base64ElevationTable}\")';"
    WriteToFile('static/tmpStaticResources.js', content)    
###########################################################################################################################    
def GeraStaticIcon(name):
    wr.wLog(f"GeraStaticIcon - {name}")
    nomeuser=wr.UserData.nome
    fileIcon = f'static/{name}.png'  
    base64ElevationTable = wr.FileToDataUrlBase64(fileIcon)
    content = f"img{name} = '{base64ElevationTable}';"
    WriteToFile('static/tmpStaticResources.js', content)     
###########################################################################################################################
def GeraMapaLeaflet(mapa,RouteDetail,static=False):
    wr.wLog(f"GeraMapaLeaflet - {mapa}")

    GeraStaticIcon("OpenElevTable") 
    GeraStaticIcon("OrdemPontos")
    GeraStaticIcon("PointerNorte")
    GeraStaticIcon("Pointer")   
    GeraStaticIcon("GpsInativo")
    GeraStaticIcon("GpsAtivo")
    GeraStaticIcon("Kml")
    
    # GeraElevationTable()    
    tmpstaticResources = ""
    if static:
       # tmpstaticResources = AbrirArquivoComoString("static/tmpStaticResources.js") 
       staticResources = AbrirArquivoComoString("static/StaticResources.js")  
       utilMap = AbrirArquivoComoString("static/UtilMap.js") 
       sDivOrdenaPontos = AbrirArquivoComoString("static/clDivOrdenaPontos.js") 
    else:
       # tmpstaticResources = "<script src=\"{{ url_for('static', filename='tmpStaticResources.js') }}\"></script>" 
       # tmpstaticResources = AbrirArquivoComoString("static/tmpStaticResources.js") 
       staticResources = "<script src=\"{{ url_for('static', filename='StaticResources.js') }}\"></script> "    
       utilMap = "<script src=\"{{ url_for('static', filename='UtilMap.js') }}\"></script>"
       sDivOrdenaPontos = "<script src=\"{{ url_for('static', filename='clDivOrdenaPontos.js') }}\"></script>"
       
       
    header = GeraHeader()
    footer = GeraFooter()
    tilesMap0 = """
            var map = L.map('map').setView([-22.9035, -43.1034], 13);
            var globalMaxElevation = """ + str(wr.MaxAltitude ) +""";
            var globalMinElevation = """ + str(wr.MinAltitude ) +""";
            var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            });
            
            var tiles2 =L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
            {
                maxZoom: 19,
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            });
            
            // Adiciona camada de tiles com elevação (exemplo: OpenTopoMap)
            // var tiles3 =L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            //     maxZoom: 10,
            //     attribution: '© OpenTopoMap contributors'
            // }).addTo(map);
            
            // Adiciona a camada padrão (OpenStreetMap)
            tiles.addTo(map);
            // Cria o controle de camadas
            var baseLayers = {
                "OpenStreetMap": tiles,
                "Satelite": tiles2,
            };

            // Adiciona o controle de camadas ao mapa
            // Adiciona o controle de camadas ao mapa no canto inferior direito
            // L.control.layers(baseLayers, null, { position: 'bottomright' }).addTo(map);
            L.control.scale({
               metric: true, // Mostrar em metros
               imperial: false, // Desativar milhas
                position: 'bottomleft' // Posição da escala
            }).addTo(map);
            </script>
            
            """    
    tilesMap1 = """
            <script>
            // Cria o marcador inicial no centro do mapa
            // const gpsMarker = L.marker([0, 0], { icon: gpsIcon }).addTo(map).bindPopup("Sua localização");
            """
    if static:
       tilesMap =  tilesMap0 + " <script> "+tmpstaticResources+ staticResources + utilMap + sDivOrdenaPontos + "</script>" + tilesMap1 
    else:
       tilesMap =  tilesMap0 + " <script> "+tmpstaticResources + "</script>" +   staticResources + utilMap + sDivOrdenaPontos + tilesMap1       
    
    texto = header + tilesMap + RouteDetail.mapcode  + footer
   
    # Abre o arquivo em modo de escrita, sobrescrevendo o conteúdo
    with open(mapa, "w", encoding="utf-8") as arquivo:
       arquivo.write(texto)
    return
###########################################################################################################################