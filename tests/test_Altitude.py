###########################################################################################################################
# Adiciona o caminho do diretório raiz ao sys.path
import os
import sys

# Caminho relativo da pasta "tests" para "webdir"
relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "backend", "webdir"))
# Adiciona o caminho ao sys.path
sys.path.append(relative_path)

import WebRota as wr

# Exemplo de uso
latitude = -15.7942  # Exemplo de latitude (Brasília)
longitude = -47.8822  # Exemplo de longitude (Brasília)

altitude = wr.getElevationOpenElev(latitude, longitude)
print(f"Altitude: {altitude} metros")

###########################################################################################################################