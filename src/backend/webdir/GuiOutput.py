#!/usr/bin/env python3
"""

"""

import json



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


    def criar_json_routing(self):
        routes_buf = [
                {
                    "routeId": "abc",
                    "automatic": True,
                    "created": "15/04/2025 13:58:49",
                    "origin": {
                    "lat": 2.802119,
                    "lng": -60.688691,
                    "elevation": 77,
                    "description": "DEDED Roraima"
                    },
                    "waypoints": [
                    {
                        "lat": 2.812482,
                        "lng": -61,
                        "elevation": 122,
                        "status": True,
                        "description": "ABC"
                    },
                    {
                        "lat": 2.840826,
                        "lng": -60.8,
                        "elevation": 29,
                        "status": True,
                        "description": "DEF"
                    },
                    {
                        "lat": 2.854428,
                        "lng": -60.7,
                        "elevation": 82,
                        "status": True,
                        "description": "GHI"
                    }
                    ],
                    "paths": [
                    [
                        [
                        2.80214,
                        -60.68868
                        ],
                        [
                        2.80144,
                        -60.68735
                        ],
                        [
                        2.80124,
                        -60.68696
                        ],        
                
                    ]
                    ]
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

