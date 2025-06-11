import webRota as wr

from functools import wraps

def ignorar_se_inativo(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "ativo", True):
            wr.wLog(f"Bypass: {func.__name__} ignorado porque self.ativo=False", level="debug")
            return self  # mantém encadeamento de chamadas
        return func(self, *args, **kwargs)
    return wrapper


class WebrotasJsOutput:
    def __init__(self, ativo=True):
        self.mapcode = ""
        self.ativo = ativo

    def append_mapcode(self, trecho: str):
        """
        Adiciona um trecho ao mapcode, como uma 'soma' de código JavaScript.
        Ignora se bypass estiver ativo.
        """
        if not self.ativo:
            return
        self.mapcode += trecho + "\n"

    @ignorar_se_inativo
    def DesenhaComunidades(self, polylinesComunidades):
        self.mapcode += f"listComunidades = [\n"
        indPol = 0
        for polyline in polylinesComunidades:
            i = 0
            self.mapcode += f"[\n"
            for coordenada in polyline:
                # wLog(f"Latitude: {coordenada[1]}, Longitude: {coordenada[0]}")  # Imprime (lat, lon)
                lat, lon = coordenada
                if i == len(polyline) - 1:  # Verifica se é o último elemento
                    self.mapcode += f"[{lat}, {lon}]\n"
                else:
                    self.mapcode += f"[{lat}, {lon}],"
                i = i + 1
            if indPol == len(polylinesComunidades) - 1:  # Verifica se é o último elemento
                self.mapcode += f"]\n"
            else:
                self.mapcode += f"],\n"
            indPol = indPol + 1
        self.mapcode += f"];\n"

        self.mapcode += f"let polyComunidades = [];"
        i = 0
        for polyline in polylinesComunidades:
            self.mapcode += f"polyTmp = L.polygon(listComunidades[{i}], {{ color: 'rgb(102,0,204)',fillColor: 'rgb(102,0,204)',fillOpacity: 0.3, weight: 1}}).addTo(map);\n"
            self.mapcode += f"polyComunidades.push(polyTmp);\n"
            i = i + 1
        return self
    
    @ignorar_se_inativo
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

    @ignorar_se_inativo
    def ServerSetupJavaScript(self,ServerTec):
        if ServerTec == "OSMR":
            self.mapcode += f"    const ServerTec = 'OSMR';\n"
            self.mapcode += f"    const UserName = '{wr.UserData.nome}';\n"
            self.mapcode += f"    const OSRMPort = {wr.UserData.OSMRport};\n"
        return self



# Instância global
# import WebrotasJsOutput as wo    



