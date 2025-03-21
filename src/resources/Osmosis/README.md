https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

3. Excluir áreas complexas (polígonos específicos)

Se você precisa excluir uma área específica definida por um polígono (como uma cidade ou um estado), use um arquivo .poly. O Osmosis suporta arquivos .poly para filtrar regiões com precisão.
A. Criar o arquivo .poly

Um arquivo .poly define os limites da área. Exemplo de um arquivo chamado exclusion.poly:

exclusion_area
   0   -43.105  -22.905
   1   -43.089  -22.917
   2   -43.044  -22.938
   3   -43.084  -22.866
END

No arquivo .poly, cada linha de coordenadas é composta por longitude e latitude (nessa ordem). Esse formato segue o padrão usado no OpenStreetMap.
Formato básico de uma linha no arquivo .poly

<índice> <longitude> <latitude>

B. Usar o filtro com .poly

Use o comando --bounding-polygon para excluir áreas fora ou dentro do polígono.

Exemplo:

osmosis --read-pbf file="map.osm.pbf" \
  --bounding-polygon file="exclusion.poly" completeWays=no \
  --write-pbf file="map_filtered.osm.pbf"


podman run --rm -v /home/user/osm-data:/data openstreetmap/osmosis \
  osmosis --read-pbf file="/data/map.osm.pbf" \
          --bounding-polygon file="/data/exclusion.poly" completeWays=no \
          --write-pbf file="/data/map_filtered.osm.pbf"


podman run --rm -v .:/data openstreetmap/osmosis \
  osmosis --read-pbf file="/data/map.osm.pbf" \
          --bounding-polygon file="/data/exclusion.poly" completeWays=no \
          --write-pbf file="/data/map_filtered.osm.pbf"



O comando que você forneceu usa a opção --rm, que faz com que o container seja removido automaticamente após a execução. Para salvar o estado do container localmente, você precisa ajustar o comando para que o container não seja removido automaticamente, permitindo que você o transforme em uma imagem ou o reutilize posteriormente.

Aqui estão os passos:
1. Rodar o container sem --rm

Execute o container sem a opção --rm para que ele permaneça no estado "parado" após a execução.

podman run -v .:/data yagajs/osmosis osmosis --read-pbf file="/data/brazil/brazil-latest.osm.pbf" --bounding-polygon file="/data/exclusion.poly" completeWays=no --write-pbf file="/data/filtro/filtro-latest.osm.pbf"

2. Salvar o container como uma imagem

Depois que o container finalizar a execução, você pode transformá-lo em uma imagem para salvar localmente.

    Liste os containers:

podman ps -a

Encontre o ID ou o nome do container associado à execução do comando.

Crie uma imagem a partir do container:

    podman commit <CONTAINER_ID> minha-imagem-osmosis

    Isso criará uma nova imagem chamada minha-imagem-osmosis, que você poderá reutilizar.

3. Usar a imagem salva

Agora que você salvou o container como uma imagem, pode reutilizá-la:

    Execute um novo container baseado na imagem:

    podman run minha-imagem-osmosis

4. Exportar a imagem para um arquivo (opcional)

Se você deseja salvar a imagem como um arquivo local para backup ou compartilhamento, pode exportá-la para um arquivo .tar:

podman save -o minha-imagem-osmosis.tar minha-imagem-osmosis

Para carregar a imagem novamente no futuro, use:

podman load -i minha-imagem-osmosis.tar

Com essas etapas, você pode salvar o estado do container e reutilizá-lo ou exportá-lo conforme necessário. 😊
