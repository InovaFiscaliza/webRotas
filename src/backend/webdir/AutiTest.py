###########################################################################################################################
import WebRota as wr

# Exemplo de uso
latitude = -15.7942  # Exemplo de latitude (Brasília)
longitude = -47.8822  # Exemplo de longitude (Brasília)

altitude = wr.getElevationOpenElev(latitude, longitude)
print(f"Altitude: {altitude} metros")

###########################################################################################################################