from wlog import wLog
###########################################################################################################################
class ClRouteDetailList:
    def __init__(self):
        self.list = []
        self.ind = 0
        self.coordinates = []
        self.pontosvisitaDados = []
        self.mapcode = ""
        self.pontoinicial = None
        self.DistanceTotal = 0
        self.cWrJsOut = None
        
    # ---------------------------------------------------
    def GeraMapPolylineCaminho(self):
        wLog("Plotando polyline rota")
        self.mapcode += "\n"

        self.mapcode += """var polylineRotaDat = ["""
        for ind, poliLine in enumerate(self.coordinates):
            self.mapcode += """["""
            for i, (lat, lon) in enumerate(poliLine):
                if i == len(poliLine) - 1:  # Último elemento
                    self.mapcode += f"[{lat}, {lon}]"
                else:
                    self.mapcode += f"[{lat}, {lon}], "
            if ind == len(self.coordinates) - 1:  # Último elemento
                self.mapcode += """]"""
            else:
                self.mapcode += """],"""
        self.mapcode += """];"""

        self.mapcode += """
            poly_lineRota = [];
            for (let i = 0; i < polylineRotaDat.length; i++) 
            {            
                var tempBuf = L.polyline(polylineRotaDat[i], {
                "bubblingMouseEvents": true,"color": "blue","dashArray": null,"dashOffset": null,
                "fill": false,"fillColor": "blue","fillOpacity": 0.2,"fillRule": "evenodd","lineCap": "round",
                "lineJoin": "round","noClip": false,"opacity": 0.7,"smoothFactor": 1.0,"stroke": true,
                "weight": 3}).addTo(map);\n
                    poly_lineRota.push(tempBuf);    
            }
            ListaRotasCalculadas[0].polylineRotaDat = polylineRotaDat;    
        """
        return
    
    ###########################################################################################################################