[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/InovaFiscaliza/webRotas)

# webRotas

O webRotas é uma ferramenta de gerenciamento de rotas de veículos utilizada em atividades de inspeção da ANATEL. A aplicação permite gerar rotas a partir de diferentes estratégias de distribuição de pontos de interesse:

- PONTOS: calcula rotas que passem no entorno de um conjunto de pontos sob análise, como estações de telecomunicações. Para tanto, é necessário definir explicitamente os pontos a serem visitados.
- GRID: calcula rotas no entorno de pontos regularmente distribuídos em forma de grade em uma localidade. Para tanto, é necessário indicar a localidade de interesse e se a rota deve se restringir à área urbanizada.
- CÍRCULO: calcula rotas no entorno de pontos dispostos circularmente ao redor de um ponto central. Para tanto, é necessário definir o ponto central, além do raio e do espaçamento entre os pontos.

<img width="2802" height="1872" alt="webRotas" src="https://github.com/user-attachments/assets/652c51fb-bf4d-4546-bb4d-18b0bfd44dc4" />


#### TIPOS DE REQUISIÇÕES
O webRotas aceita três tipos principais de requisições, cada uma gerando rotas através de estratégias distintas. Todas as requisições devem seguir o formato JSON e conter os campos obrigatórios: `type`, `origin` e `parameters`.

##### 1. Tipo "shortest" - Rota entre Pontos Específicos
Gera uma rota otimizada passando pelos pontos de interesse definidos explicitamente (waypoints). Ideal para inspecionar locais específicos como estações de telecomunicações.

**Campos obrigatórios:**
- `type`: "shortest"
- `origin`: Ponto de partida com latitude, longitude e descrição
- `parameters.waypoints`: Array de pontos a serem visitados

**Exemplo de requisição:**
```json
{
    "type": "shortest",
    "origin": {
        "lat": -22.902368,
        "lng": -43.174200,
        "description": "Anatel-RJ"
    },
    "parameters": {
        "waypoints": [
            {
                "lat": -22.510099,
                "lng": -43.175840,
                "description": "Petrópolis"
            },
            {
                "lat": -22.417852,
                "lng": -42.973280,
                "description": "Teresópolis"
            },
            {
                "lat": -22.281154,
                "lng": -42.532454,
                "description": "Nova Friburgo"
            }
        ]
    },
    "avoidZones": [],
    "criterion": "duration"
}
```

##### 2. Tipo "circle" - Rota em Padrão Circular
Gera uma rota em torno de um ponto central com pontos de interesse distribuídos circularmente. Útil para cobertura sistemática em torno de uma localização central.

**Campos obrigatórios:**
- `type`: "circle"
- `origin`: Ponto de partida com latitude, longitude e descrição
- `parameters.centerPoint`: Ponto central (latitude e longitude)
- `parameters.radius`: Raio em quilômetros
- `parameters.totalWaypoints`: Quantidade de pontos na distribuição circular

**Exemplo de requisição:**
```json
{
    "type": "circle",
    "origin": {
        "lat": -22.902368,
        "lng": -43.174200,
        "description": "Anatel-RJ"
    },
    "parameters": {
        "centerPoint": {
            "lat": -22.910555,
            "lng": -43.163606
        },
        "radius": 10,
        "totalWaypoints": 21
    },
    "avoidZones": [],
    "criterion": "duration"
}
```

##### 3. Tipo "grid" - Rota em Padrão de Grade
Gera uma rota em torno de pontos regularmente distribuídos em forma de grade dentro de uma localidade. Ideal para inspeção sistemática de uma região urbana.

**Campos obrigatórios:**
- `type`: "grid"
- `origin`: Ponto de partida com latitude, longitude e descrição
- `parameters.city`: Nome da cidade
- `parameters.state`: Sigla do estado (UF)
- `parameters.scope`: "Location" para área urbana ou "City" para cidade inteira
- `parameters.pointDistance`: Distância em metros entre os pontos da grade

**Exemplo de requisição:**
```json
{
    "type": "grid",
    "origin": {
        "lat": -22.902368,
        "lng": -43.174200,
        "description": "Anatel-RJ"
    },
    "parameters": {
        "city": "Rio de Janeiro",
        "state": "RJ",
        "scope": "Location",
        "pointDistance": 10000
    },
    "avoidZones": [],
    "criterion": "duration"
}
```

#### CAMPOS OPCIONAIS

**avoidZones**: Array de zonas a serem evitadas na rota. Cada zona é um polígono definido por coordenadas.

```json
"avoidZones": [
    {
        "name": "Parque da Cidade",
        "coord": [
            [-22.920469, -43.093928],
            [-22.921399, -43.088298],
            [-22.923394, -43.082380],
            [-22.929908, -43.078627]
        ]
    }
]
```

**criterion**: Critério de otimização da rota (padrão: "duration")
- "duration": Otimiza pelo tempo de viagem
- "distance": Otimiza pela distância total

**closed**: Indica se a rota será fechada ou não, caso `true` é definida o origem com ponto final da rota
- "true": "Fecha" a rota, i.e. **adiciona a origem como ponto final também**
- "false": Faz o roteamento normal com os pontos definidos na requisição, sem fechar a rota

**endpoint**: Ponto final opcional (_Esse ponto final deve ser necessariamente um dos pontos da rota e não um novo ponto_)
```json
"endpoint": 
    {
        "description": "Parque da Cidade",
        "lat": -22.920469, 
        "lng": -43.093928,
            
    }
```
> ⚠️Somente uma das opções `"closed": "true"` OU `"endpoint": ...` é aceita, passar ambas chaves implica em erro.



#### ARQUIVOS DE TESTES
Na pasta `tests` há diversos tipos de exemplos de requisições

## INSTALAÇÃO E EXECUÇÃO

O webRotas oferece três opções de instalação e execução, cada uma com diferentes características e capacidades de roteamento.

Importante: As opções 1 e 2 NÃO incluem o contêiner OSRM. Nesses modos, a aplicação ficará limitada a consultas na API Pública do OpenStreetMap, o que pode resultar em rotas menos otimizadas e sujeitas a limites de uso. Para habilitar o OSRM local e obter desempenho/qualidade superiores, utilize a opção 3 (Docker Compose).

### Opção 1: Instalação local para desenvolvimento (uv)

Ideal para desenvolvimento, testes e depuração.

1) Instale o uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

Verifique:
```bash
uv --version
```

2) Clone o repositório
```bash
git clone https://github.com/InovaFiscaliza/webRotas.git
cd webRotas
```

3) Sincronize o ambiente
```bash
uv sync
# Para desenvolvimento (inclui dependências de teste)
uv sync --dev
```

4) Execute o servidor FastAPI
```bash
uv run --directory src uvicorn webrotas.main:app --host 127.0.0.1 --port 5002
# Alternativa
uv run src/webrotas/main.py --port 5002
```

Acesse:
- App: http://127.0.0.1:5002
- Docs (Swagger): http://127.0.0.1:5002/docs
- ReDoc: http://127.0.0.1:5002/redoc


Testes:
```bash
uv run pytest tests/
uv run pytest tests/test_fastapi.py
uv run python tests/test_fastapi.py
uv run python tests/test_logging.py
```

Limitação desta opção: sem contêiner OSRM, a aplicação depende da API Pública do OSM.

### Opção 2: Construir e executar a imagem Docker (sem OSRM)

Ideal para empacotar e rodar apenas a API FastAPI em um contêiner.

1) Build da imagem
```bash
docker build -t webrotas:latest .
```

2) Run do contêiner
```bash
docker run -d \
  --name webrotas \
  -p 5002:5002 \
  -e PYTHONUNBUFFERED=1 \
  webrotas:latest
# (Opcional) Limites de recursos
# --memory=4g --cpus=4
```

Acesse:
- App: http://localhost:5002
- Docs: http://localhost:5002/docs

Logs e parada:
```bash
docker logs -f webrotas
docker stop webrotas && docker rm webrotas
```

Limitação desta opção: sem contêiner OSRM, a aplicação depende da API Pública do OSM.

### Opção 3: Docker Compose (recomendado, com OSRM)

Implantação completa com OSRM local e pré-processamento automatizado dos dados OSM.

Pré-requisitos:
- Docker e Docker Compose v2+
- ~40GB livres em disco (dados + preprocessing)
- Recomendado: 32GB RAM

1) Configure variáveis de ambiente (.env)
```bash
# Diretório para dados do OSRM
OSRM_DATA=/caminho/para/osrm-data

# Limites (opcionais)
OSRM_PREP MEMORY_LIMIT=32g
OSRM_PREP_CPU_LIMIT=8
OSRM_MEMORY_LIMIT=16g
OSRM_CPUS_LIMIT=4.0
APP_MEMORY_LIMIT=4g
APP_CPUS_LIMIT=4.0
```
Exemplo criando o diretório dentro do projeto:
```bash
mkdir -p ./osrm-data
# no .env
OSRM_DATA=$(pwd)/osrm-data
```

2) Suba a stack
```bash
docker-compose up -d --build
```
Ordem de inicialização:
1. osrm-init: baixa dados do Brasil (se necessário, via MD5) e executa osrm-extract/partition/customize
2. osrm: sobe o roteador em http://localhost:5000
3. webrotas: sobe a API em http://localhost:5002

Em execuções futuras (com cache válido), o preprocessing é pulado automaticamente.

3) Acesso e operação
- App: http://localhost:5002
- OSRM: http://localhost:5000
- Docs: http://localhost:5002/docs

Monitorar e gerenciar:
```bash
# Logs
docker-compose logs -f
# Logs individuais
docker-compose logs -f osrm-init
docker-compose logs -f osrm
docker-compose logs -f webrotas
# Status
docker-compose ps
# Parar/destruir
docker-compose stop
docker-compose down
# Remover tudo (incl. volumes)
docker-compose down -v
```

Dados OSRM:
```bash
# Tamanho dos dados
du -sh $OSRM_DATA
# Arquivos gerados
ls -lh $OSRM_DATA/
# Reprocessar do zero (apaga dados)
rm -rf $OSRM_DATA/*
# próxima execução fará novo download/preprocessamento
docker-compose up -d --build
```
