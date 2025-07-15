
import wlog as wl
import datetime
import webRota as wr
###########################################################################################################################
from functools import wraps

def ignorar_se_inativo(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "ativo", True):
            wl.wLog(f"Bypass: {func.__name__} ignorado porque self.ativo=False", level="debug")
            return self  # mantém encadeamento de chamadas
        return func(self, *args, **kwargs)
    return wrapper
###########################################################################################################################
def get_formatted_timestamp():
    now = datetime.datetime.now()
    return now.strftime("%Y/%m/%d_%H:%M:%S")
###########################################################################################################################
class ClRouteDetailList:
    def __init__(self, ativo=True):
        self.ativo = ativo
        self.list = []
        self.ind = 0
        self.coordinates = []
        self.pontosvisitaDados = []
        self.mapcode = ""
        self.pontoinicial = None
        self.DistanceTotal = 0
        self.tempo_total = 0
        self.cWrJsOut = None

        
    # ---------------------------------------------------------------------------------------
    @ignorar_se_inativo
    def GeraMapPolylineCaminho(self):
        wl.wLog("Plotando polyline rota")
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
    # ---------------------------------------------------------------------------------------
    def append_mapcode(self, trecho: str):
        """
        Adiciona um trecho ao mapcode, como uma 'soma' de código JavaScript.
        Ignora se bypass estiver ativo.
        """
        if not self.ativo:
            return
        self.mapcode += trecho + "\n"
    # ---------------------------------------------------------------------------------------
    @ignorar_se_inativo
    def DeclaraArrayRotas(self):
        # var estruturas = []; // Array vazio
        # Salvar
        # sessionStorage.setItem('sessionId', 'abc123');
        # // Recuperar
        # const sessionId = sessionStorage.getItem('sessionId');
        # AAAAAAAAAAAAAAAAAAAAAAAa
        timeStp = get_formatted_timestamp()
        output = ""
        output += f"    var ListaRotasCalculadas = [];\n"
        output += f"    var bufdados = {{}};\n"
        output += f"    bufdados.id = 0;\n"
        output += f"    bufdados.time = '{timeStp}';\n"
        output += f"    bufdados.polylineRotaDat = [];\n"
        output += f"    bufdados.pontosvisitaDados = pontosvisitaDados;\n"
        output += (
            f"    bufdados.pontosVisitaOrdenados = pontosVisitaOrdenados;\n"
        )
        output += f"    bufdados.pontoinicial = [{self.pontoinicial[0]},{self.pontoinicial[1]},'{self.pontoinicial[2]}'];\n"
        output += f"    bufdados.DistanceTotal = {self.DistanceTotal / 1000};\n"
        output += f"    bufdados.tempo_total = '{self.tempo_total}';\n"
        
        output += (
            f"    bufdados.rotaCalculada = 1;\n"  # Rota calculada pelo WebRotas
        )
        output += f"    ListaRotasCalculadas.push(bufdados);\n"

        self.append_mapcode(output)
        return 



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
        wl.wLog("Plotando Regiões de mapeamento e exclusões")

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
            wl.wLog(f"  Região: {nome}", level="debug")
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


###########################################################################################################################