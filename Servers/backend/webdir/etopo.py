import WebRota as wr

# -22.919802062945383, -43.043920503331314  - 378 m   Mirante do cantagalo

lat = -22.919802062945383
lon = -43.043920503331314 
alt=wr.AltitudeOpenElevation(lat,lon)

print(f"Altitude {lat},{lon} - {alt}")


###########################################################################################################################
# Gerar a imagem
# wr.generate_elevation_table_png(output_filename='elevation_table.png',max_elevation=1500)


# teste=wr.FileToDataUrlBase64("static/GpsAtivo.png")
# print(teste)