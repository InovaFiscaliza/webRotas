# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

webRotas is a vehicle route management tool used for ANATEL (Brazilian National Telecommunications Agency) inspection activities. It's a Flask-based web application that calculates routes for visiting specific points using different distribution strategies:

- **PONTOS (Points)**: Routes passing near specific analysis points (telecommunication stations)
- **GRID**: Routes around regularly distributed grid points in a locality  
- **CÍRCULO (Circle)**: Routes around points arranged circularly around a central point

The application processes geospatial data, calculates optimal routes using OSRM (Open Source Routing Machine), and provides elevation information.

## Architecture Overview

### Core Components

- **Backend Server** (`src//`): Flask-based REST API server
  - `server.py`: Main Flask application with route endpoints
  - `web_rotas.py`: Core routing logic for different route types
  - `route_request_manager.py`: Manages route request lifecycle
  - `api_routing.py` & `api_elevation.py`: External API integrations
  - `routing_servers_interface.py`: Container/OSRM server management

- **Client Interface** (`src/ucli/`): Command-line client for server interaction
  - `webrota_client.py`: CLI client for sending requests
  - `server_interface.py`: Server communication abstraction
  - `json_validate.py`: Request validation logic

- **Static Assets** (`src//static/`): Web frontend (HTML/CSS/JS)

- **Data Resources** (`src/resources/`): Geospatial reference data
  - Brazilian municipal boundaries, urban areas, street networks (OSM data)
  - Container images for routing services (Osmosis, OSRM)

### Technology Stack

- **Python 3.11** with UV package manager
- **Flask** web framework with CORS and compression
- **Geospatial**: GeoPandas, Shapely, GeoPy for geographic operations
- **Routing**: OSRM backend via containers (Podman)
- **Data Processing**: NumPy, PyArrow for performance
- **Containerization**: Podman for routing service isolation

## Common Development Commands

### Environment Setup
```powershell
# Install dependencies and create virtual environment
uv sync

# Install dependencies for development (includes test dependencies)  
uv sync --dev
```

### Running the Application
```powershell
# Start the Flask development server
uv run src//server.py

# Start server with custom port
uv run src//server.py --port 5003

# Run client with example payload
uv run src/ucli/webrota_client.py tests/request_shortest\ \(RJ\).json

# Run client without arguments (shows help + demo)
uv run src/ucli/webrota_client.py
```

### Testing
```powershell
# Run all tests (when pytest is added as dev dependency)
uv run pytest tests/

# Run specific test file
uv run pytest tests/dev/test_Funcionalidades.py

# Run individual development test scripts
uv run tests/dev/test_Altitude.py
```

### Development Workflow
```powershell
# Launch server in debug mode (VSCode configuration available)
# Use .vscode/launch.json configurations for debugging

# Validate request payloads
uv run src/ucli/json_validate.py path/to/request.json

# Test server connectivity
curl "http://127.0.0.1:5002/ok?sessionId=test"
```

## Request Types & API Structure

The server accepts JSON requests with the following structure:

- **Required fields**: `type`, `origin`, `parameters`
- **Optional fields**: `avoidZones`, `criterion`

### Supported Route Types
1. **shortest**: Direct routing between specific waypoints
2. **circle**: Points arranged in circle around center point
3. **grid**: Grid-based points within city boundaries
4. **ordered**: Custom route with predefined cache/bounding box

### API Endpoints
- `POST /process?sessionId=<id>`: Main route processing endpoint
- `GET /ok?sessionId=<id>`: Health check endpoint
- `GET /` or `/webRotas`: Serves static web interface

## Data Dependencies

The application requires large geospatial datasets (~2.3GB) containing:
- Brazilian municipal boundaries (IBGE 2023)
- Urban areas and communities (IBGE)
- Street network data (OpenStreetMap via Geofabrik)

These are typically downloaded from ANATEL's internal SharePoint or public repositories during installation.

## Container Services

webRotas uses containerized services for routing:
- **Osmosis**: OSM data preprocessing
- **OSRM Backend**: Route calculation engine

Services are managed via Podman and initialized during first setup.

## Development Notes

- The codebase uses Portuguese comments and variable names (ANATEL context)
- Route calculations are cached using bounding box-based cache system
- The application is Windows-focused but uses WSL/containers for compatibility
- Static files are served directly by Flask in development mode
- All Python execution should use `uv run` commands for proper environment management
- Test files in `tests/` directory contain both JSON request examples and Python test scripts