# Port Configuration Refactoring

## Overview
Deprecated the `src/webrotas/port_test.py` module and refactored the codebase to read port configurations from a `.env` file using `python-dotenv`.

## Changes Made

### 1. Created `.env` File
**Location**: `/home/ronaldo/Work/webRotas/.env`

Configuration options:
- `WEBROTAS_PORT`: Port for the webRotas FastAPI server (default: 5003)
- `OSRM_PORT`: Port for the OSRM routing service (default: 5000)
- `WEBROTAS_ENVIRONMENT`: Environment type - "development" or "production" (default: development)
- `OSRM_HOSTNAME`: Optional custom OSRM hostname
- `WEBROTAS_HOSTNAME`: Optional custom webRotas hostname

```env
# Server Configuration
WEBROTAS_PORT=5003
OSRM_PORT=5000

# Environment type (development or production)
WEBROTAS_ENVIRONMENT=development

# Custom hostnames (optional - defaults to localhost/container names based on environment)
# OSRM_HOSTNAME=osrm
# WEBROTAS_HOSTNAME=webrotas
```

### 2. Refactored `src/webrotas/server_env.py`
**Changes**:
- Removed dependency on `webrotas.port_test` module
- Added `python-dotenv` import for environment variable loading
- Reads `WEBROTAS_PORT` and `OSRM_PORT` from `.env` file at initialization
- Added `.env` file path resolution (3 levels up from module)
- Stored both `webrotas_port` and `osrm_port` as instance attributes
- Added `port` property for backward compatibility with command-line argument handling
- Updated `save_server_data()` to store both port values

**Key Methods**:
```python
@property
def port(self) -> int:
    """Get the webRotas server port."""
    return self.webrotas_port

@port.setter
def port(self, value: int) -> None:
    """Set the webRotas server port."""
    self.webrotas_port = value
```

### 3. Updated `src/webrotas/main.py`
**Changes**:
- Removed `env.get_port(args.port)` call that used port availability checking
- Replaced with direct port assignment if command-line argument differs from configured port
- Ports are now read from `.env` at startup and can be overridden via CLI arguments

```python
# Before
env.get_port(args.port)

# After
if args.port != env.port:
    env.port = args.port
```

### 4. Updated `pyproject.toml`
**Added dependency**:
```toml
"python-dotenv>=1.0.0",
```

### 5. Deleted `src/webrotas/port_test.py`
Removed the deprecated port availability checking module. This module is no longer needed since ports are now configured explicitly via `.env` file.

## File Changes Summary

| File | Change | Status |
|------|--------|--------|
| `.env` | Created | ✅ New |
| `src/webrotas/server_env.py` | Refactored to use python-dotenv | ✅ Updated |
| `src/webrotas/main.py` | Removed port availability check | ✅ Updated |
| `src/webrotas/route_request_manager.py` | No changes (still imports server_env) | ✅ Unaffected |
| `src/webrotas/port_test.py` | Deleted | ✅ Removed |
| `pyproject.toml` | Added python-dotenv dependency | ✅ Updated |

## Migration Notes

### For Development
1. The `.env` file is checked in with sensible defaults
2. Developers can create a `.env.local` if needed (make sure to add to `.gitignore`)
3. Environment variables can still be overridden via command line: `uv run --directory src uvicorn webrotas.main:app --port 5003`

### For Production/Containerized Environments
1. Set `WEBROTAS_ENVIRONMENT=production` in `.env` or Docker build
2. Container hostnames are automatically used when `WEBROTAS_ENVIRONMENT=production`
3. Explicit port configuration avoids runtime port availability issues

### Backward Compatibility
- Command-line `--port` arguments still work and override `.env` settings
- The `ServerEnv.port` property maintains compatibility with existing code
- No changes required in consumer code (e.g., `route_request_manager.py`)

## Testing
Verified port loading from `.env` file:
```bash
$ cd /home/ronaldo/Work/webRotas
$ uv run python -c "from src.webrotas.server_env import env; print(f'webRotas port: {env.webrotas_port}'); print(f'OSRM port: {env.osrm_port}')"
webRotas port: 5003
OSRM port: 5000
```

## Benefits
1. **Explicit Configuration**: Ports are no longer dynamically searched; they're explicitly configured
2. **Environment Management**: Easy to switch between development, staging, and production configurations
3. **Container Friendly**: Works seamlessly with container orchestration and environment variable passing
4. **Reduced Complexity**: Removes port availability checking logic that could cause issues in containerized environments
5. **Consistency**: OSRM port is now managed alongside webRotas port in a unified configuration system
