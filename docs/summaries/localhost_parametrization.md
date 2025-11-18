# Localhost Parametrization Implementation

## Overview
All hardcoded references to `localhost` and `127.0.0.1` have been parametrized to support both development and containerized environments.

## Key Changes

### 1. New Configuration Module
**File**: `src/webrotas/config/server_hosts.py`

Central configuration module for managing host addresses across environments:
- **Development**: Uses `localhost`/`127.0.0.1`
- **Containerized**: Uses container hostnames (`osrm`, `webrotas`)

**Environment Variables**:
- `WEBROTAS_ENVIRONMENT`: Set to `'development'` (default) or `'production'`
- `OSRM_HOSTNAME`: Custom OSRM hostname (default: `'osrm'` in production, `'localhost'` in development)
- `WEBROTAS_HOSTNAME`: Custom webRotas hostname (default: `'webrotas'` in production, `'localhost'` in development)

**Key Functions**:
```python
get_osrm_host()          # Returns OSRM server hostname
get_webrotas_host()      # Returns webRotas server hostname
get_osrm_url(port)       # Returns full OSRM URL
get_webrotas_url(port)   # Returns full webRotas URL
is_containerized()       # Returns environment type
```

### 2. Backend Updates

#### `src/webrotas/api_routing.py`
- Updated `is_port_available()`: Now uses `get_osrm_host()` by default
- Updated `get_osrm_matrix_from_local_container()`: Uses parametrized host for container requests
- Updated `get_osrm_route()`: Uses parametrized host for local container routing

#### `src/webrotas/route_request_manager.py`
- Updated `create_initial_route()`: Uses `get_webrotas_url()` instead of hardcoded `http://127.0.0.1:port/`

#### `src/webrotas/routing_servers_interface.py`
- Updated `find_available_port()`: Added optional `host` parameter
- Updated `VerificarOsrmAtivo()`: Uses parametrized OSRM hostname

#### `src/webrotas/ucli/server_interface.py`
- Updated `update_url_port()`: Dynamically constructs URLs using `get_webrotas_host()`
- SERVER_ROOT_URL now set dynamically instead of hardcoded

### 3. Frontend Updates

#### `src/webrotas/static/js/webRotas.js`
- Updated `server.url` initialization: Now determined dynamically using `window.location.hostname`
- Works for both:
  - **Development**: Served from `localhost:5001` → uses `http://localhost:5001`
  - **Containerized**: Served from container hostname → uses `http://<container-hostname>:5001`

## Environment Setup

### Development Mode (Default)
No environment variables needed; defaults to localhost:
```bash
# Development - uses localhost automatically
uv run src/webrotas/server.py
```

### Containerized Mode
Set environment variables before running:
```bash
# Containerized - use container hostnames
export WEBROTAS_ENVIRONMENT=production
export WEBROTAS_HOSTNAME=webrotas
export OSRM_HOSTNAME=osrm
docker-compose up
# or
podman-compose up
```

## Files Modified

1. ✅ `src/webrotas/config/server_hosts.py` (NEW)
2. ✅ `src/webrotas/api_routing.py`
3. ✅ `src/webrotas/route_request_manager.py`
4. ✅ `src/webrotas/routing_servers_interface.py`
5. ✅ `src/webrotas/ucli/server_interface.py`
6. ✅ `src/webrotas/static/js/webRotas.js`

## Testing Checklist

- [ ] Test development mode: `uv run src/webrotas/server.py`
- [ ] Verify localhost URLs work in browser at `http://localhost:5002`
- [ ] Test containerized deployment with `docker-compose` or `podman-compose`
- [ ] Verify container-to-container communication using service names
- [ ] Verify frontend can communicate with backend using correct hostname
- [ ] Verify OSRM container detection works in both environments
- [ ] Run test suite to ensure no regressions

## Benefits

1. **Flexibility**: Single codebase works in both development and production
2. **Docker/Podman Ready**: Proper hostname resolution in container networks
3. **Environment-aware**: Configuration adapts automatically to deployment context
4. **Easy Configuration**: Simple environment variables for customization
5. **Backward Compatible**: Defaults to development mode if no env vars set

## Future Considerations

- Consider centralizing all port numbers in the configuration module
- Add validation for environment variables
- Consider adding logging for URL construction in debug mode
- Test with Kubernetes deployment if needed
- Consider service discovery mechanisms for dynamic container discovery
