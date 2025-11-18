# Resumo da Implementação de Zonas de Evitação

## Problema

O sistema webRotas precisava suportar **zonas de evitação** - áreas geográficas que as rotas devem evitar ou minimizar passar através delas. O desafio principal era uma limitação fundamental do OSRM: **alternativas de rotas só funcionam para requisições com 2 coordenadas (origem-destino)**, não para rotas com múltiplos pontos de parada (3+ coordenadas).

## Solução Implementada

### 1. **Alternativas Baseadas em Segmentos** 

Para requisições multi-ponto com zonas de evitação:

- **Decompõe** a rota em segmentos de 2 coordenadas (A→B, B→C, C→D)
- **Solicita alternativas** de cada segmento em paralelo do OSRM
- **Combina** as alternativas de segmentos em rotas completas
- **Pontu a** cada rota baseado em penalidades por intersecção com zonas

**Benefício:** Habilita alternativas para rotas multi-ponto, que o OSRM não suporta nativamente.

### 2. **Roteamento Ciente de Zonas**

Quando todas as alternativas baseadas em segmentos ainda cruzam zonas de evitação:

- **Gera pontos de referência** ao redor do perímetro da zona em distâncias progressivas (1.5km, 3km, 5km, 7.5km, 10km)
- **Tenta rotas** através de pontos de referência únicos e pareados
- **Seleciona a melhor alternativa** com menor pontuação de penalidade (melhoria de 10%+ necessária)

**Benefício:** Tenta encontrar rotas que minimizem sobreposição de zona através de inserção dinâmica de pontos de parada.

### 3. **Correção de Requisições httpx**

Corrigiu requisições HTTP assíncronas para lidar adequadamente com parâmetros URL:

```python
# ANTES (incorreto):
response = await client.get(url, params=params)

# DEPOIS (correto):
request_url = httpx.URL(url, params=params)
response = await client.get(request_url)
```

**Por que importa:** URLs da API OSRM já contêm parâmetros de query. Usar `httpx.URL()` garante manipulação apropriada de parâmetros.

## Fluxo de Integração

### Na função `get_osrm_route()`:

1. **Detecta** requisições multi-ponto (3+) com zonas de evitação
2. **Usa alternativas baseadas em segmentos** como abordagem principal
3. **Volta para roteamento ciente de zona** se todas as alternativas cruzam zonas
4. **Prioriza** rotas por pontuação de penalidade (menos sobreposição = melhor)
5. **Retorna** rotas com metadados detalhados de penalidade

### Formato de Resposta:

Cada rota inclui informações de penalidade:

```json
{
  "geometry": {...},
  "distance": 27950,
  "duration": 2212,
  "penalties": {
    "zone_intersections": 1,
    "penalty_score": 0.0316
  }
}
```

## Limitações

### Limitação Fundamental

Quando uma zona de evitação grande bloqueia geometricamente o caminho direto entre pontos de parada obrigatórios, **OSRM ainda roteará através dela** porque é o caminho otimizado. Isso é inevitável sem perfis de evitação baseados em pré-processamento.

### O Que Funciona Bem

- Cenários onde **algumas alternativas evitam zonas melhor que outras**
- Rotas com **múltiplas zonas** que não bloqueiam completamente caminhos
- Fornecimento de **visibilidade** sobre métricas de intersecção de zona

### Limitações do OSRM

- **Máximo 3 alternativas** por requisição
- **Apenas requisições com 2 coordenadas** para alternativas
- Não pode realmente "forçar" evitação sem pré-processamento

## Módulos Criados

- `domain/routing/alternatives.py` - Alternativas baseadas em segmentos
- `domain/routing/zone_aware.py` - Roteamento ciente de zona
- Modificações em `infrastructure/routing/osrm.py` - Integração e correção httpx

## Testes Criados

1. `test_integration.py` - Testa alternativas baseadas em segmentos
2. `test_zone_aware.py` - Testa roteamento ciente de zona com cenário Osasco
3. `test_httpx_fix.py` - Verifica manipulação de parâmetros URL httpx

## Resultados

✓ Implementação completa de alternativas para rotas multi-ponto com zonas
✓ Correção de requisições HTTP assíncronas para API pública
✓ Suporte para priorização e visualização de penalidades de zona
✓ Testes de validação para todos os módulos principais
