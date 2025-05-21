#!/usr/bin/env python3
"""

"""

import json



class GuiOutput:
    def __init__(self):
        self.json = ""  
        self.jsonComunities = None  
    
    def jsonComunitiesCreate(self, polylinesComunidades):
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

        # Gera JSON apenas da lista com indentação
        json_array = json.dumps(urban_communities, indent=2)

        # Monta manualmente com a chave (sem as chaves externas)
        self.jsonComunities = f'"urbanCommunities": {json_array}'

        # Salva no arquivo
        # with open("temp.json", "w", encoding="utf-8") as f:
        #    f.write(self.jsonComunities)

        # Retorna a string gerada
        return self.jsonComunities

    

    
    
# Instância global
cGuiOutput = GuiOutput()

