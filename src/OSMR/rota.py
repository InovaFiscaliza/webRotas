# pip install requests polyline folium


import requests
import folium
import polyline

# Coordenadas de início e fim   
start_coords = (-22.914135986040844, -43.17767870155183)
end_coords = (-22.917110304492653, -43.09170799646564)

# URL da solicitação OSRM
url = f"http://localhost:5000/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline"

# Fazer a solicitação
response = requests.get(url)
data = response.json()

# Verificar se a solicitação foi bem-sucedida
if response.status_code == 200 and 'routes' in data:
    route = data['routes'][0]
    geometry = route['geometry']
    coordinates = polyline.decode(geometry)

    # Criar o mapa
    mapa = folium.Map(location=start_coords, zoom_start=14)

    # Adicionar a rota ao mapa
    folium.PolyLine(locations=coordinates, color='blue', weight=5).add_to(mapa)

    # Adicionar marcadores de início e fim
    folium.Marker(location=start_coords, popup='Início', icon=folium.Icon(color='green')).add_to(mapa)
    folium.Marker(location=end_coords, popup='Fim', icon=folium.Icon(color='red')).add_to(mapa)

    # Salvar o mapa como um arquivo HTML
    mapa.save('rota.html')
    print("Mapa salvo como 'rota.html'")
else:
    print(f"Erro na solicitação: {data}")

