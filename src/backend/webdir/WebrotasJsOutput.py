import webRota as wr

class WebrotasJsOutput:
    def __init__(self):
        self.mapcode = ""


    def DesenhaRegioes(self, regioes):
        # Processa as regiões
        wr.wLog("Plotando Regiões de mapeamento e exclusões")

        RegiaoExclusão = False
        for regiao in regioes:
            nome = regiao.get("nome", "Sem Nome").replace(" ", "")
            if "!" in nome:
                nome = nome.replace("!", "")
                RegiaoExclusão = True
            else:
                RegiaoExclusão = False

            self.mapcode += f"    regiao{nome} = [\n"
            coordenadas = regiao.get("coord", [])
            wr.wLog(f"  Região: {nome}", level="debug")
            i = 0
            for coord in coordenadas:
                latitude, longitude = coord
                if i == len(coordenadas) - 1:  # Verifica se é o último elemento
                    self.mapcode += f"       [{latitude}, {longitude}]\n"
                else:
                    self.mapcode += f"       [{latitude}, {longitude}],"
                i = i + 1
            self.mapcode += f"    ];\n"
            if RegiaoExclusão:
                self.mapcode += f"var polygon{nome} = L.polygon(regiao{nome}, {{ color: 'red',fillColor: 'lightred',fillOpacity: 0.2, weight: 1}}).addTo(map);\n"
            else:
                self.mapcode += f"var polygon{nome} = L.polygon(regiao{nome}, {{ color: 'green',fillColor: 'lightgreen',fillOpacity: 0.0, weight: 1}}).addTo(map);\n"
        return self

# Instância global
# import WebrotasJsOutput as wo    
cWrJsOut = WebrotasJsOutput()


