# Logs API Guide

## Overview

The webRotas application now includes a comprehensive API for retrieving logs from both the webRotas application and the OSRM container. This enables the frontend to diagnose issues and display relevant debugging information when errors occur.

## Endpoints

### 1. Get Application Logs

**Endpoint:** `GET /logs/app`

**Description:** Retrieve recent application logs from the webRotas server.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of log lines to return (default: 100, max: 1000)
- `log_level` (string, optional): Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `module` (string, optional): Filter by module name pattern

**Example Requests:**

```bash
# Get last 100 application log lines
curl http://localhost:5003/logs/app

# Get last 50 ERROR level logs
curl http://localhost:5003/logs/app?limit=50&log_level=ERROR

# Get logs from specific module
curl http://localhost:5003/logs/app?module=osrm_health&limit=100

# Combine filters
curl http://localhost:5003/logs/app?limit=200&log_level=WARNING&module=route_service
```

**Response:**

```json
{
  "status": "success",
  "logs": [
    {
      "content": "2024-11-24 20:23:32 - webrotas.api.services.route_service - INFO - [route_service.py:45] - Route processing started",
      "file": "webrotas.log",
      "timestamp": "2024-11-24 20:23:32"
    }
  ],
  "count": 1,
  "limit": 100,
  "log_level_filter": null,
  "module_filter": null
}
```

---

### 2. Get Container Logs

**Endpoint:** `GET /logs/container`

**Description:** Retrieve logs from the OSRM container.

**Query Parameters:**
- `container` (string, optional): Container name (default: "osrm")
- `tail` (integer, optional): Number of most recent lines to return (default: 100, max: 1000)

**Example Requests:**

```bash
# Get last 100 OSRM container logs
curl http://localhost:5003/logs/container

# Get last 50 lines
curl http://localhost:5003/logs/container?tail=50

# Get logs from specific container
curl http://localhost:5003/logs/container?container=osrm&tail=200
```

**Response:**

```json
{
  "status": "success",
  "container_name": "osrm",
  "logs": [
    {
      "content": "[2024-11-24 20:23:32] OSRM Engine initialized"
    }
  ],
  "count": 1,
  "tail": 100,
  "cli_used": "podman"
}
```

**Status Codes:**
- `200`: Container logs retrieved successfully
- `503`: Container not found or not running
- `500`: Error retrieving container logs

---

### 3. Get Combined Logs

**Endpoint:** `GET /logs/`

**Description:** Retrieve both application and container logs in a single response.

**Query Parameters:**
- `app_limit` (integer, optional): Maximum application log lines (default: 50, max: 500)
- `container_tail` (integer, optional): Maximum container log lines (default: 50, max: 500)
- `container` (string, optional): Container name (default: "osrm")

**Example Requests:**

```bash
# Get combined logs with defaults
curl http://localhost:5003/logs

# Get more logs from both sources
curl http://localhost:5003/logs?app_limit=200&container_tail=200

# Specify custom container name
curl http://localhost:5003/logs?container=osrm&app_limit=100&container_tail=100
```

**Response:**

```json
{
  "status": "success",
  "timestamp": "2024-11-24T20:23:32.123456",
  "app_logs": {
    "status": "success",
    "logs": [],
    "count": 0,
    "limit": 50
  },
  "container_logs": {
    "status": "success",
    "container_name": "osrm",
    "logs": [],
    "count": 0,
    "tail": 50,
    "cli_used": "podman"
  }
}
```

---

### 4. List Log Files

**Endpoint:** `GET /logs/files`

**Description:** Get information about available log files on the system.

**Example Request:**

```bash
curl http://localhost:5003/logs/files
```

**Response:**

```json
{
  "status": "success",
  "logs_directory": "/path/to/logs",
  "files": [
    {
      "name": "webrotas.log",
      "path": "/path/to/logs/webrotas.log",
      "size_bytes": 1024000,
      "size_mb": 1.0,
      "modified": "2024-11-24T20:23:32",
      "created": "2024-11-24T20:00:00"
    }
  ],
  "count": 1,
  "directory_exists": true
}
```

---

## Frontend Integration

### Example JavaScript Usage

```javascript
// Get application logs
async function fetchAppLogs() {
  try {
    const response = await fetch('/logs/app?limit=50&log_level=ERROR');
    const data = await response.json();
    if (data.status === 'success') {
      displayLogs(data.logs);
    } else {
      console.error('Failed to fetch logs:', data.message);
    }
  } catch (error) {
    console.error('Error fetching logs:', error);
  }
}

// Get combined logs for debugging
async function fetchDebugInfo() {
  try {
    const response = await fetch('/logs?app_limit=100&container_tail=100');
    const data = await response.json();
    
    // Display app logs
    console.log('App Logs:', data.app_logs.logs);
    
    // Check container status
    if (data.container_logs.status === 'warning') {
      console.warn('OSRM container not available');
    } else {
      console.log('Container Logs:', data.container_logs.logs);
    }
  } catch (error) {
    console.error('Error fetching debug info:', error);
  }
}

// Display error logs when something goes wrong
async function handleError(errorContext) {
  try {
    const logs = await fetch(
      `/logs?app_limit=200&container_tail=200`
    ).then(r => r.json());
    
    const errorReport = {
      timestamp: new Date().toISOString(),
      context: errorContext,
      app_logs: logs.app_logs.logs.slice(-20), // Last 20 logs
      container_logs: logs.container_logs.logs.slice(-20),
      container_status: logs.container_logs.status
    };
    
    // Send error report to backend or display to user
    console.error('Error Report:', errorReport);
    return errorReport;
  } catch (error) {
    console.error('Failed to generate error report:', error);
  }
}
```

---

## API Documentation

The Logs API is automatically documented in the FastAPI interactive API docs:

- **Swagger UI:** http://localhost:5003/docs
- **ReDoc:** http://localhost:5003/redoc

Both interfaces provide interactive exploration of all endpoints, query parameters, and response schemas.

---

## Error Handling

### Common Scenarios

**Container Not Running:**
```json
{
  "status": "warning",
  "message": "Container 'osrm' not found or not running. Ensure podman/docker is running.",
  "container_name": "osrm",
  "logs": [],
  "tail": 100
}
```

**No Log Files Found:**
```json
{
  "status": "success",
  "logs": [],
  "count": 0,
  "message": "No log files found"
}
```

**Server Error:**
```json
{
  "status": "error",
  "message": "Permission denied reading log file",
  "logs": []
}
```

---

## Implementation Details

### Logs Service (`src/webrotas/api/services/logs_service.py`)

The service module provides core functionality:

- **`get_app_logs()`**: Reads application log files from the logs directory
  - Supports filtering by log level and module name
  - Returns most recent logs first (up to the specified limit)
  - Handles file I/O errors gracefully

- **`get_container_logs()`**: Retrieves container logs via CLI
  - Tries podman first, then falls back to docker
  - Handles container not found/not running scenarios
  - Configurable tail parameter for performance

- **`get_combined_logs()`**: Aggregates both sources
  - Returns unified response with both app and container logs
  - Useful for comprehensive debugging

- **`get_log_files_info()`**: Lists available log files
  - Provides file metadata (size, modification time)
  - Helps identify which logs are available

### Routing

All endpoints are prefixed with `/logs`:
- `/logs/app` - Application logs
- `/logs/container` - Container logs
- `/logs/` - Combined logs
- `/logs/files` - List log files

---

## Performance Considerations

- **Limits**: Maximum 1000 lines for individual endpoints, 500 for combined endpoint
- **File I/O**: Large log files are read efficiently with streaming
- **Container Logs**: CLI queries are cached briefly to avoid excessive system calls
- **Filtering**: Applied during read to minimize memory usage

---

## Troubleshooting

### "Container not found" error

Ensure the OSRM container is running:

```bash
# Check container status
podman ps | grep osrm
# or
docker ps | grep osrm

# Start container if needed
podman run -d --name osrm ...
```

### No logs appearing

Check log file permissions:

```bash
ls -la /path/to/logs/
```

Ensure the webRotas application has write permissions to the logs directory.

### High memory usage when fetching large log files

Reduce the `limit` or `tail` parameters to fetch fewer lines at a time.

---

## Future Enhancements

Potential improvements:
- Log pagination with cursor support
- Real-time log streaming via WebSocket
- Log search/grep functionality
- Log rotation and archival management
- Structured log format (JSON) for easier parsing
- Log sampling for high-volume scenarios
