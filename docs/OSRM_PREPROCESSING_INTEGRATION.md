# OSRM Preprocessing Integration

## Overview

The OSRM preprocessing steps have been integrated into the Docker Compose stack through a dedicated initialization service (`osrm-init`). This ensures that preprocessing happens automatically before the OSRM routing engine starts, eliminating the need for manual preprocessing.

## Architecture

### Service Dependency Chain

```
osrm-init (runs once, exits on completion)
    ↓
osrm (waits for init to complete successfully)
    ↓
webrotas (waits for osrm to be healthy)
```

## Components

### 1. Dockerfile.osrm-init

A dedicated Dockerfile that creates the preprocessing initialization container:

- **Base Image**: `python:3.13-slim-bookworm`
- **Tools**: Includes Docker CLI and curl for downloading OSM data
- **Entrypoint**: Runs `osrm-preprocessing.py` script
- **Volumes**: Mounts the OSRM data directory and Docker socket

### 2. Updated docker-compose.yml

#### osrm-init Service

```yaml
osrm-init:
  build:
    context: .
    dockerfile: Dockerfile.osrm-init
  container_name: osrm-init
  environment:
    - OSRM_DATA=${OSRM_DATA:-/data}
  volumes:
    - ${OSRM_DATA}:/data
    - /var/run/docker.sock:/var/run/docker.sock:rw
  restart: no
  deploy:
    resources:
      limits:
        memory: ${INIT_MEMORY_LIMIT:-2g}
```

**Key Features:**
- Runs only once (no restart policy)
- Has read-write access to Docker socket (needed to run preprocessing Docker containers)
- Memory limited to 2GB by default (can be overridden via `INIT_MEMORY_LIMIT`)

#### osrm Service (Updated)

```yaml
osrm:
  image: ghcr.io/project-osrm/osrm-backend:latest
  # ... other config ...
  depends_on:
    osrm-init:
      condition: service_completed_successfully
```

**Change:** Added dependency on `osrm-init` with `service_completed_successfully` condition to ensure it only starts after preprocessing is complete.

#### webrotas Service (Updated)

```yaml
webrotas:
  # ... other config ...
  depends_on:
    osrm:
      condition: service_healthy
```

**Change:** Now uses `service_healthy` condition (instead of just `service_started`) to ensure OSRM is fully ready before webrotas starts.

## Preprocessing Workflow

When `docker-compose up` is executed:

1. **osrm-init container starts** and runs `osrm-preprocessing.py`:
   - Checks remote MD5 hash of Brazil OSM data from Geofabrik
   - Compares with local file (if exists)
   - Downloads latest OSM data only if needed (smart caching)
   - Runs three OSRM preprocessing commands:
     - `osrm-extract`: Converts OSM to intermediate format
     - `osrm-partition`: Creates partition tables for MLD algorithm
     - `osrm-customize`: Optimizes for fast queries
   - Renames output files from `region.osm.*` to `brazil-latest.osm.*`
   - Exits with success code

2. **osrm container starts** (only after osrm-init exits successfully):
   - Uses the preprocessed `brazil-latest.osm` files
   - Loads routing data and starts the OSRM routing engine
   - Exposes port 5000 for routing requests

3. **webrotas container starts** (only after osrm is healthy):
   - Connects to OSRM at http://osrm:5000
   - Serves the web interface on port 5002

## Environment Variables

Add these to your `.env` file to customize behavior:

```bash
# Data directory (required)
OSRM_DATA=/path/to/osrm/data

# Resource limits (optional, use defaults if not set)
INIT_MEMORY_LIMIT=2g
OSRM_MEMORY_LIMIT=16g
OSRM_CPUS_LIMIT=4.0
APP_MEMORY_LIMIT=4g
APP_CPUS_LIMIT=4.0
```

## Usage

### First Run (with preprocessing)

```bash
docker-compose up
```

The init service will:
1. Download Brazil OSM data (~800MB)
2. Run preprocessing pipeline (varies: 30min - 2 hours depending on hardware)
3. Exit successfully
4. OSRM and webrotas will then start

### Subsequent Runs (cached)

If OSM data hasn't changed (same MD5):
- Init service detects local file is up-to-date
- Skips download and preprocessing
- Exits immediately
- OSRM and webrotas start quickly

## Benefits

1. **Automated**: No manual preprocessing required
2. **Smart Caching**: Only downloads/processes if data changed
3. **Dependency Management**: Docker Compose ensures correct startup order
4. **Resource Controlled**: Separate memory limits for each service
5. **Failure Handling**: If preprocessing fails, OSRM won't start (preventing errors later)
6. **Monitoring**: Clear logs showing each preprocessing step

## Troubleshooting

### Init Service Fails

Check logs:
```bash
docker-compose logs osrm-init
```

Common issues:
- **No disk space**: Ensure ~40GB free (for data + preprocessing)
- **No internet**: Required to download OSM data from Geofabrik
- **Docker socket issue**: Ensure Docker is running and socket is accessible

### OSRM Doesn't Start

Check if init completed:
```bash
docker-compose logs osrm-init | tail -20
```

Verify data files exist:
```bash
ls -lh ${OSRM_DATA}/brazil-latest.osm.*
```

### Performance Issues

- Increase `INIT_MEMORY_LIMIT` if preprocessing is slow
- Ensure `OSRM_DATA` is on fast storage (SSD preferred)
- Check system resources: `docker stats`

## Related Files

- `Dockerfile.osrm-init`: Initialization container definition
- `docker-compose.yml`: Service orchestration
- `scripts/osrm-preprocessing.py`: Preprocessing logic
- `scripts/osrm-preprocessing.sh`: Bash version of preprocessing
