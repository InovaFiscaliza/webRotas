#!/usr/bin/env python3
"""

"""

import json



class GuiOutput:
    def __init__(self):
        self.json = ""  
        self.jsonComunities = None  
    
    def jsonComunitiesCreate(self,polylinesComunidades):
        """
        Gera uma string JSON formatada com as comunidades urbanas a partir de listas de coordenadas.
        
        :param polylinesComunidades: Lista de listas de coordenadas. Cada sublista representa um polígono,
                                    onde cada coordenada é uma tupla/lista (lat, lon).
        :return: String JSON formatada com indentação.
        """
        # Reestrutura os dados se estiverem como [(lat, lon)] e não [[lon, lat]]
        urban_communities = []
        for polyline in polylinesComunidades:
            community = []
            for coord in polyline:
                lat, lon = coord
                community.append([lat, lon])
            urban_communities.append(community)
        
        output_dict = {"urbanCommunities": urban_communities}
        self.jsonComunities = json.dumps(output_dict, indent=2)
        
        with open("temp.json", "w", encoding="utf-8") as f:
             f.write(self.jsonComunities)
        
        return self.jsonComunities

    

    
    
# Instância global
cGuiOutput = GuiOutput()

