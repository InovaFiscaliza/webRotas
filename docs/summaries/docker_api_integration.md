# Docker API Integration Implementation

## Overview
Implemented a Docker API client wrapper to replace subprocess-based CLI calls for container operations. This provides a more robust, type-safe, and reusable interface for managing Docker containers and running commands.

## Changes Made

### 1. New Docker Infrastructure Module
**Location:** `src/webrotas/infrastructure/docker/`

#### `docker_client.py` - Core Docker API Wrapper
High-level abstraction over the official `docker-py` library:

**Key Classes:**
- `DockerAPIClient`: Main client class with container operations
- `DockerClientError`: Base exception for Docker operations
- `ContainerNotFoundError`: Specific exception for missing containers
- `ContainerCommandError`: Exception for command execution failures

**Methods:**
- `get_container(name)`: Get container object by name
- `get_container_logs(name, tail, follow)`: Retrieve container logs
- `container_exists(name)`: Check if container exists
- `container_is_running(name)`: Check container status
- `exec_command(name, cmd, user, workdir)`: Execute commands in containers
- `list_containers(all)`: List all or running containers
- `get_container_info(name)`: Get detailed container information

**Singleton Pattern:**
- `get_docker_client()`: Provides a singleton instance for reuse across the application

#### `__init__.py` - Module Exports
Exports all public classes and functions for clean imports.

### 2. Refactored Logs Service
**Location:** `src/webrotas/api/services/logs_service.py`

**Changes:**
- Replaced subprocess-based Docker CLI calls with Docker API
- Improved error handling with specific exception types
- Cleaner, more maintainable code
- Better error messages for diagnostics

**Benefits:**
- No dependency on external CLI tools
- Proper exception handling with specific error types
- Can be used in containerized environments
- Easier to extend for other container operations

### 3. Updated Dependencies
**File:** `pyproject.toml`

Added `docker>=7.0.0` to the project dependencies. This is the official Python Docker SDK maintained by Docker.

## Usage Examples

### Getting Container Logs
```python
from webrotas.infrastructure.docker import get_docker_client

docker_client = get_docker_client()
logs = docker_client.get_container_logs("osrm", tail=100)
print(logs)
```

### Executing Commands in Container
```python
result = docker_client.exec_command(
    "osrm",
    command=["ls", "-la"],
    workdir="/data"
)
print(f"Exit code: {result['exit_code']}")
print(f"Output: {result['stdout']}")
```

### Checking Container Status
```python
if docker_client.container_is_running("osrm"):
    print("OSRM is running")
else:
    print("OSRM is not running")
```

## Architecture Advantages

1. **Reusability**: The Docker client can be used throughout the application for various container operations
2. **Type Safety**: Proper exception types for different failure scenarios
3. **Singleton Pattern**: Efficient resource usage with a single shared client
4. **Decoupling**: No dependency on CLI tool availability
5. **Testability**: Easier to mock Docker operations in tests
6. **Error Handling**: Specific exceptions allow for targeted error handling
7. **Extensibility**: Easy to add new methods for other Docker operations

## Error Handling

The implementation provides specific exception types:
- `ContainerNotFoundError`: Container doesn't exist
- `ContainerCommandError`: Command execution failed
- `DockerClientError`: General Docker client errors

This allows callers to handle different failure scenarios appropriately.

## Future Enhancements

The Docker client can be extended to support:
- Container lifecycle management (start, stop, restart)
- Image management
- Network operations
- Volume management
- Container resource monitoring
- Streaming logs
- Building images from Dockerfiles

All these operations would follow the same clean API pattern established here.
