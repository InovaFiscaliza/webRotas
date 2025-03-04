# NOTAS SOBRE ENTRADAS E SAÍDAS Eric

## Entradas:

- **Polígono do Mapa**:Criar uma rotina que o defina automaticamente. (p.e.: os limites de LAT e LONG formam um polígono, extrapolam-se esses limites em 50 km para N, S, E e W, e usa esse mapa como referência). Importante aqui é ter um cache que analise os pontos de interesse e verifique se eles estão contidos nos mapas em cache. (implantada)
- **Polígonos de Exclusão**:Criar a possibilidade de inserir diretamente os vértices (num JSON, como é hoje) ou receber um KML com um ou mais polígonos desenhados ali no Google Earth, por exemplo.
- **Polígono de Interesse da Localidade**:
  Criar a possibilidade de passar o nome da localidade (num JSON, como é hoje) ou um KML. Verificar o formato exportado pelo Mosaico, por exemplo, com o contorno protegido (se é que isso existe).

## Saídas:

- HTML (já implantada)
- KML (implantada)
- Arquivo para importar em ferramentas de navegação (explorar MapsME, MyMaps etc)

---

# NOTAS SOBRE O PROCESSAMENTO

## ASPECTOS PRIORITÁRIOS (penso):

1. **Definir Ponto Inicial da Rota**:Talvez evoluir o HTML, criando um painel que apresenta a ordem de execução da rota, possibilitando definir o seu ponto inicial (por meio de um dropdown). Como a rota azul é estática, e isso o JS do HTML offline não vai recalcular, imagino que uma saída seria criar uma "rota fechada", que começa e termina no mesmo ponto, passando por todos os outros.Algo como: `P1 > P2 > P3 > P4 > P1`. Se o cara indicar `P3` como ponto inicial, então seria `P3 > P4 > P1 > P2 > P3` e por aí vai... O que quero sugerir é que o HTML continue estático e seja funcional, mesmo sem o servidor rodando ao fundo.
2. **Inserir Tag nos Ícones dos Pontos de Interesse**:P1, P2, P3, etc.   (Tag implementado esperando avaliação)
3. **Alterar Ícone com Proximidade**:
   Criar código em JS que mude o ícone dos pontos quando o veículo se aproximar deles.

## ASPECTOS NÃO PRIORITÁRIOS (mas importantes):

1. **Obter a Elevação dos Pontos de Interesse**:Depois de definidos os pontos de interesse que nortearão a rota, obter a elevação de cada um, usando essa informação como forma de definir as cores do ícone (ao invés do azul estático).
2. **Métrica de Distância Mínima Aceitável**:Avaliar a inclusão de métrica de distância mínima aceitável entre a rota e os pontos de interesse, evitando sair das vias principais para "tocar" nos pontos.
3. **Interface Gráfica**:
   Interface gráfica para dar maior fluidez à interface com a a

# Funcionalidades e Requisitos Notas do Lobão

- Exportar KML
- Definir ponto de início
- Definir sequência de execução (ordem da rota)
- Não repetir ruas
- Incluir/excluir pontos e recalcular rota completa (azul)
- Acesso ao app à partir do navegador veicular (AndroidAuto/Screenshare)
- Descrever procedimento de carga de dados gerados para aplicações de navegação (google)
- Integrar dados de elevação do terreno (apresentação da elevação na cor do navegador)
- Pontos e polígonos baseados na elevação do terreno. (pontos mais altos ou mais baixos de uma região)
- Importação de contornos protegidos de radiodifusores
- Integração com RF.DataHub
- Navegação inter-municipal
- Para integração no appColeta, considerar multiView, manter o serviço para acesso pelo motorista em paralelo com a apresentação para o fiscal.
- Repositório de polígonos editados por usuários


Requisitos ultima reunião sexta pré carnaval - 28/02/2025

* Mudar nome da pasta de "Servers" para "src". OK
* Migrar "images" para "docs/images" e ajustar path do Readme.md. OK
* Migrar arquivos testes "Test.py", "Test1.py" e "Test2.py" para pasta "tests".
* Migrar arquivos de suporte ao código para uma subpasta "src/resources". Por exemplo: "src/resources/IBGE" ou "src/resources/Docker" etc (não lembro os nomes exatamente). Ajustar os paths dos arquivos que os requisitam. OK
* Eliminar todo e qualquer experimento que não é abarcado na versão atual da aplicação. OK

Outro ponto é que os arquivos de testes sejam descritivos e comecem com `test_` . Tipo `test_<funcionalidade>.py`. Assim bibliotecas de teste identificam automaticamente. Em python nenhum arquivo ou pasta começa com caixa alta...isso é coisa de outras linguagens.
