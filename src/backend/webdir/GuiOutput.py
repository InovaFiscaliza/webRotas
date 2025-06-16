#!/usr/bin/env python3
""" """

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

    @property
    def pontoinicial(self):
        return self._pontoinicial

    @pontoinicial.setter
    def pontoinicial(self, value):
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            rounded = self.round_coords(value[:2])
            self._pontoinicial = rounded + list(value[2:])
        else:
            self._pontoinicial = value

    def round_coords(self, coord):
        """Helper method to round coordinates to 6 decimal places"""
        if isinstance(coord, (list, tuple)):
            return [round(float(x), 6) if x is not None else None for x in coord]
        return round(float(coord), 6) if coord is not None else None

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
                community.append(self.round_coords([lat, lon]))
            urban_communities.append(community)
        self.jsonComunities = urban_communities
        return self.jsonComunities

    def gerar_waypoints(self, pontosvisitaDados):
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

            waypoints.append(
                {
                    "lat": lat,
                    "lng": lng,
                    "elevation": elevation,
                    "status": status,
                    "description": description,
                }
            )
        return waypoints

    def criar_json_routing(self):
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        waypoints = self.gerar_waypoints(self.pontosvisitaDados)
        self.estimated_distance = round(self.estimated_distance / 1000, 1)

        # Round coordinates in waypoints_route
        rounded_paths = []
        if self.waypoints_route:
            for path in self.waypoints_route:
                rounded_path = []
                for coord in path:
                    rounded_path.append(self.round_coords(coord))
                rounded_paths.append(rounded_path)

        # Round coordinates in bounding_box
        rounded_bounding_box = []
        if self.bounding_box:
            for coord in self.bounding_box:
                rounded_bounding_box.append(self.round_coords(coord))

        # Round coordinates in limits
        rounded_limits = []
        if self.limits:
            for limit_group in self.limits:
                rounded_group = []
                for coord in limit_group:
                    rounded_group.append(self.round_coords(coord))
                rounded_limits.append(rounded_group)

        # Round coordinates in urbanAreas
        rounded_urban_areas = []
        if self.urbanAreas:
            for area in self.urbanAreas:
                rounded_area = []
                for coord in area:
                    rounded_area.append(self.round_coords(coord))
                rounded_urban_areas.append(rounded_area)

        routes_buf = [
            {
                "routeId": "abc",
                "automatic": True,
                "created": f"{data}",
                "origin": {
                    "lat": round(float(self.pontoinicial[0]), 6),
                    "lng": round(float(self.pontoinicial[1]), 6),
                    "elevation": 0,
                    "description": f"{self.pontoinicial[2]}",
                },
                "waypoints": waypoints,
                "paths": rounded_paths,
                "estimatedDistance": self.estimated_distance,
            }
        ]

        estrutura = {
            "url": self.url,
            "routing": [
                {
                    "request": self.requisition_data,
                    "response": {
                        "cacheId": f"{self.cache_id}",
                        "boundingBox": rounded_bounding_box,
                        "location": {
                            "limits": rounded_limits,
                            "urbanAreas": rounded_urban_areas,
                            "urbanCommunities": self.jsonComunities,
                        },
                        "routes": routes_buf,
                    },
                }
            ],
        }

        json_formatado = json.dumps(estrutura, indent=4, ensure_ascii=False)

        # Salvar em arquivo (opcional)
        # with open("routingZZZZ.json", "w", encoding="utf-8") as f:
        #    f.write(json_formatado)

        return json_formatado


# Instância global
cGuiOutput = GuiOutput()
