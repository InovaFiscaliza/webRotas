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
- "true": "Fecha" a rota, i.e. define a origem como ponto final também
- "false": Faz o roteamento normal com os pontos definidos na requisição, sem fechar a rota

**endpoint**: Ponto final opcional (_Esse ponto final deve ser necessariamente um dos pontos da rota e não um novo ponto)
```json
"endpoint": 
    {
        "description": "Parque da Cidade",
        "lat": -22.920469, 
        "lng": -43.093928,
            
    }
```



#### ARQUIVOS DE TESTES
Na pasta `tests` há diversos tipos de exemplos de requisições
