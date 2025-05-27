#!/usr/bin/env python3
"""

"""

import json
from datetime import datetime


class GuiOutput:
    def __init__(self):
        self.json = ""  
        self.jsonComunities = None  
        self.requisition_data = None
        self.url = ""
        self.cache_id = None
        self.bounding_box = None
        self.session_id = None
        self.limits = None
        self.urbanAreas = None
        self.pontoinicial = None
        self.pontosvisitaDados = None
        self.waypoints_route = None
        self.estimated_distance = None

    
    def json_comunities_create(self, polylinesComunidades):
        """
        Gera uma string com o conteúdo de urbanCommunities formatado como JSON,
        mas sem as chaves externas (sem { }).
        
        :param polylinesComunidades: Lista de listas de coordenadas (lat, lon).
        :return: String JSON no formato '"urbanCommunities": [ ... ]'
        """
        # Prepara os dados como lista de listas
        urban_communities = []
        for polyline in polylinesComunidades:
            community = []
            for coord in polyline:
                lat, lon = coord
                community.append([lat, lon])
            urban_communities.append(community)
        self.jsonComunities = urban_communities
        # Salva no arquivo
        # with open("temp.json", "w", encoding="utf-8") as f:
        #    f.write(self.jsonComunities)
        # Retorna a string gerada
        return self.jsonComunities

    
    def gerar_waypoints(self, pontosvisitaDados):
    # [-22.88169706392197, -43.10262976730735,"P0","Local", "Descrição","Altitude","Ativo"],
        waypoints = []
        for item in pontosvisitaDados:
            lat = round(float(item[0]), 6)
            lng = round(float(item[1]), 6)
            description = str(item[4])
            try:
                elevation = int(float(item[5]))
            except ValueError:
                elevation = 0  # valor padrão caso erro na conversão
            status = True

            waypoints.append({
                "lat": lat,
                "lng": lng,
                "elevation": elevation,
                "status": status,
                "description": description
            })
        return waypoints

    
    def criar_json_routing(self):
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S") 
        waypoints = self.gerar_waypoints(self.pontosvisitaDados)
        routes_buf = [
                {
                    "routeId": "abc",
                    "automatic": True,
                    "created": f"{data}",
                    "origin": {
                    "lat": round(float(self.pontoinicial[0]), 6),
                    "lng": round(float(self.pontoinicial[1]), 6),
                    "elevation": 77,
                    "description": f"{self.pontoinicial[2]}"
                    },
                    "waypoints": waypoints,
                    "paths": self.waypoints_route,
                    "estimatedDistance": self.estimated_distance
                }
            ]

        
        estrutura = {
            "url": self.url,
            "routing": [ 
                         { 
                           "request": self.requisition_data,
                           "response": {
                                        "cacheId": f"{self.cache_id}",
                                        "boundingBox": self.bounding_box,
                                        "location": 
                                        {
                                            "limits": self.limits,
                                            "urbanAreas": self.urbanAreas,
                                            f"urbanCommunities": self.jsonComunities
                                        },
                                        "routes": routes_buf 
                                        }                               
                         }
                       ]          
        }



        json_formatado = json.dumps(estrutura, indent=4, ensure_ascii=False)
        
        # Salvar em arquivo (opcional)
        with open("routingZZZZ.json", "w", encoding="utf-8") as f:
            f.write(json_formatado)

        return json_formatado
    
# Instância global
cGuiOutput = GuiOutput()

