# WebRotas Test Suite Summary

## Overview
This document describes the new test files created to expand the test coverage of the webRotas route management application across different Brazilian regions and route types.

## Test Files Structure

All test files follow the standard webRotas JSON request format with the following components:
- **type**: Route calculation type (shortest, circle, or grid)
- **origin**: Starting point with latitude, longitude, and description
- **parameters**: Route-specific parameters
- **avoidZones**: Optional polygonal zones to avoid in route calculation
- **criterion**: Optimization criterion (duration or distance)

## New Test Files Created

### 1. Shortest Route Tests

#### request_shortest (MG).json
- **Region**: Minas Gerais
- **Origin**: Belo Horizonte area (ANATEL office)
- **Waypoints**: Ouro Preto, Itabira, Sabará, Betim
- **Criterion**: Duration
- **Purpose**: Test shortest route optimization in central MG region

#### request_shortest (SP-distance).json
- **Region**: São Paulo
- **Origin**: São Paulo (ANATEL office)
- **Waypoints**: São José dos Campos, Atibaia, Pindamonhangaba, Guaratinguetá, Diadema
- **Criterion**: Distance (varies from standard duration)
- **Purpose**: Test distance-based optimization criterion with multiple waypoints in SP interior

#### request_shortest (GO-distance).json
- **Region**: Goiás
- **Origin**: Brasília area (ANATEL office)
- **Waypoints**: Goiânia, Anápolis, Itumbiara, Águas Lindas de Goiás
- **Criterion**: Distance
- **Purpose**: Test central region routing with distance optimization

#### request_shortest (AM-PA).json
- **Region**: North Region (Amazonas-Pará)
- **Origin**: Manaus (ANATEL office)
- **Waypoints**: Manaus Centro, Manacapuru, Iranduba, Belém
- **Criterion**: Duration
- **Purpose**: Test long-distance routing in the northern Amazon region

#### request_shortest (MS-avoid).json
- **Region**: Mato Grosso do Sul
- **Origin**: Campo Grande (ANATEL office)
- **Waypoints**: Campo Grande, Rio Brilhante, Dourados, Naviraí
- **AvoidZones**: 1 protection area defined
- **Criterion**: Duration
- **Purpose**: Test routing with avoid zones in central-west region

### 2. Circle Route Tests

#### request_circle (Brasília-DF).json
- **Region**: Federal District
- **Center Point**: Central Brasília
- **Radius**: 8 km
- **Total Waypoints**: 18
- **AvoidZones**: Esplanada dos Ministérios
- **Criterion**: Duration
- **Purpose**: Test circle route generation in capital city with government restricted area

#### request_circle (Salvador-BA).json
- **Region**: Bahia
- **Center Point**: Central Salvador
- **Radius**: 12 km
- **Total Waypoints**: 25
- **AvoidZones**: 2 zones (Centro Histórico, Farol da Barra)
- **Criterion**: Duration
- **Purpose**: Test circle route with multiple avoid zones in northeastern city

#### request_circle (Manaus-AM).json
- **Region**: Amazonas
- **Center Point**: Manaus center
- **Radius**: 15 km (larger radius for sparse Amazon region)
- **Total Waypoints**: 20
- **AvoidZones**: None
- **Criterion**: Duration
- **Purpose**: Test circle route generation without restrictions in Amazon region

#### request_circle (Porto Alegre-RS).json
- **Region**: Rio Grande do Sul
- **Center Point**: Porto Alegre center
- **Radius**: 10 km
- **Total Waypoints**: 22
- **AvoidZones**: Parque da Redenção
- **Criterion**: Duration
- **Purpose**: Test circle route in southern metropolitan region with park area restriction

#### request_circle (Recife-PE).json
- **Region**: Pernambuco
- **Center Point**: Recife center
- **Radius**: 9 km
- **Total Waypoints**: 19
- **AvoidZones**: Complexo da Livraria
- **Criterion**: Duration
- **Purpose**: Test circle route in northeastern coast region

### 3. Grid Route Tests

#### request_grid (Recife-PE).json
- **City**: Recife
- **State**: PE (Pernambuco)
- **Point Distance**: 8,000 meters
- **Scope**: Location
- **Purpose**: Test grid distribution in northeast coastal city with tighter spacing

#### request_grid (Fortaleza-CE).json
- **City**: Fortaleza
- **State**: CE (Ceará)
- **Point Distance**: 12,000 meters
- **Scope**: Location
- **Purpose**: Test grid distribution in larger northeastern city

#### request_grid (Curitiba-PR).json
- **City**: Curitiba
- **State**: PR (Paraná)
- **Point Distance**: 9,000 meters
- **Scope**: Location
- **Purpose**: Test grid distribution in southern metropolitan region

#### request_grid (Belo Horizonte-MG).json
- **City**: Belo Horizonte
- **State**: MG (Minas Gerais)
- **Point Distance**: 7,000 meters
- **Scope**: Location
- **Purpose**: Test grid distribution in central region with tighter spacing

#### request_grid (Manaus-AM).json
- **City**: Manaus
- **State**: AM (Amazonas)
- **Point Distance**: 15,000 meters (larger for sparse region)
- **Scope**: Location
- **Purpose**: Test grid distribution in Amazon region with wider spacing

## Geographic Coverage

### Brazilian Regions Covered

**North**
- Amazonas (AM): Manaus
- Pará (PA): Belém (in shortest route)

**Northeast**
- Pernambuco (PE): Recife
- Ceará (CE): Fortaleza
- Bahia (BA): Salvador

**Center-West**
- Federal District (DF): Brasília
- Goiás (GO): Goiânia area
- Mato Grosso do Sul (MS): Campo Grande

**Southeast**
- São Paulo (SP): São Paulo metropolitan area
- Minas Gerais (MG): Belo Horizonte area
- Rio de Janeiro (RJ): Existing tests

**South**
- Paraná (PR): Curitiba
- Rio Grande do Sul (RS): Porto Alegre

## Test Parameters Analysis

### Point Distance Variations (Grid Routes)
- **Small (7,000-8,000m)**: Dense metropolitan areas (Recife, Belo Horizonte, SP)
- **Medium (9,000-12,000m)**: Large cities (Curitiba, Fortaleza)
- **Large (15,000m)**: Sparse regions (Manaus - Amazon)

### Circle Route Radius Variations
- **Standard (8-10km)**: Urban centers
- **Medium (12km)**: Larger cities (Salvador)
- **Large (15km)**: Sparse regions (Manaus)

### Waypoint Count Variations
- **Grid Routes**: All use same calculation based on pointDistance and city boundaries
- **Circle Routes**: 18-25 waypoints depending on circle radius and city size
- **Shortest Routes**: 4-5 waypoints for typical inspection routes

## Testing Recommendations

1. **Regional Validation**: Ensure correct handling of coordinates across Brazil's vast territory
2. **Criterion Comparison**: Compare duration vs. distance optimization results
3. **AvoidZones Effectiveness**: Validate that specified zones are properly respected in routes
4. **Performance**: Monitor performance variations across different regions and route complexities
5. **Edge Cases**: Test with various pointDistance values to identify optimal spacing

## Integration with CI/CD

These test files can be integrated into automated testing workflows:
```bash
# Run all shortest route tests
for file in tests/request_shortest*.json; do
    uv run src/ucli/webrota_client.py "$file"
done

# Run all circle route tests
for file in tests/request_circle*.json; do
    uv run src/ucli/webrota_client.py "$file"
done

# Run all grid route tests
for file in tests/request_grid*.json; do
    uv run src/ucli/webrota_client.py "$file"
done
```

## Notes

- All coordinates are based on actual Brazilian city centers and ANATEL office locations
- AvoidZones use realistic polygonal definitions based on actual landmarks and protected areas
- All tests maintain compatibility with existing test structure and request validation
- Test files follow Portuguese naming conventions consistent with project standards
