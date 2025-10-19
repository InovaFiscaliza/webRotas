# webRotas Logging Configuration

## Overview

webRotas uses Python's standard `logging` module with a centralized configuration for consistent log handling across all modules. Logs are automatically saved to the `logs/` directory at the project root.

## Log Directory Structure

```
webRotas/
├── logs/
│   ├── main.log
│   ├── routing_servers_interface.log
│   └── bounding_boxes.log
```

## Features

### Dual Output
- **Console Output**: INFO level and above with color coding
- **File Output**: DEBUG level and above with detailed formatting

### Color Coding (Console)
- 🔵 **DEBUG**: Cyan
- 🟢 **INFO**: Green
- 🟡 **WARNING**: Yellow
- 🔴 **ERROR**: Red
- 🟣 **CRITICAL**: Magenta

### Log Rotation
- Maximum file size: 10 MB per log file
- Backup count: 10 previous log files retained
- Automatic rotation when size limit is reached

### Log Format

**Console Format:**
```
[LEVEL] module.name - message
```

**File Format:**
```
YYYY-MM-DD HH:MM:SS - module.name - LEVEL - [filename:lineno] - message
```

Example file log entry:
```
2025-10-18 02:38:30 - webrotas.main - INFO - [main.py:31] - This is an INFO message from main module
```

## Usage

### Basic Usage

```python
from webrotas.config.logging_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Use logging at different levels
logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # inc_info=True adds traceback
```

### In Modules

Replace the old logging setup:
```python
# OLD (Deprecated)
import logging
logger = logging.getLogger(__name__)
```

With:
```python
# NEW (Recommended)
from webrotas.config.logging_config import get_logger
logger = get_logger(__name__)
```

## Logging Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed information for debugging |
| INFO | General informational messages |
| WARNING | Warning messages for potential issues |
| ERROR | Error messages for failures |
| CRITICAL | Critical failures requiring immediate attention |

## Configuration Files

### Main Configuration Module
- **Location**: `src/webrotas/config/logging_config.py`
- **Components**:
  - `ColoredFormatter`: Adds ANSI color codes to console output
  - `setup_logging()`: Configures logging for a module
  - `get_logger()`: Convenience function to get configured logger

### Log Directory
- **Location**: Defined in `project_folders.py`
- **Path**: `<PROJECT_ROOT>/logs/`
- **Auto-created**: Yes, on first logger initialization

## Logging in Different Scenarios

### Application Startup
```python
logger.info(f"Starting FastAPI server on port {args.port}")
logger.debug("Loading configuration files")
```

### Errors with Full Traceback
```python
try:
    # operation
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

### Performance Tracking
```python
logger.debug(f"Processing request took {elapsed_time}ms")
logger.info(f"Successfully processed {count} items")
```

## Testing

Run the logging test script:
```bash
cd /home/ronaldo/Work/webRotas
uv run python src/test_logging.py
```

Expected output:
- Console: Colored log messages at INFO level and above
- Files: Log files created in `logs/` directory with DEBUG level and above

## Troubleshooting

### Logs Not Created
1. Check that `logs/` directory is writable
2. Verify `project_folders.py` correctly defines `LOGS_PATH`
3. Ensure `get_logger()` is called before logging

### Missing Debug Messages in Console
- This is expected - console output is set to INFO level
- Check the log files in `logs/` for DEBUG messages
- To change console level, modify `setup_logging()` in `logging_config.py`

### Permission Errors
```bash
# Ensure logs directory has write permissions
chmod 755 /home/ronaldo/Work/webRotas/logs
```

## Log File Management

Log files are automatically rotated based on size:
- Current log: `module_name.log`
- Rotated logs: `module_name.log.1`, `module_name.log.2`, etc.

To clean up old logs:
```bash
# Remove logs older than 30 days
find /home/ronaldo/Work/webRotas/logs -name "*.log*" -mtime +30 -delete
```

## Performance Impact

- Minimal overhead for logging operations
- File I/O is optimized with Python's `RotatingFileHandler`
- Buffer size: ~1KB per log record
- No blocking on log writes

## Best Practices

1. **Use appropriate levels**:
   - DEBUG for development/troubleshooting
   - INFO for important events
   - WARNING for potential issues
   - ERROR for failures

2. **Avoid logging sensitive data**:
   ```python
   # BAD: Don't log passwords, tokens, etc.
   logger.info(f"Login with password: {password}")
   
   # GOOD: Log only necessary information
   logger.info(f"User authentication attempt")
   ```

3. **Use structured logging**:
   ```python
   # BAD: Unstructured
   logger.info("Process started")
   
   # GOOD: Structured with context
   logger.info(f"Process started for region {region_id}")
   ```

4. **Include context in errors**:
   ```python
   logger.error(f"Failed to process file {filename}: {error}", exc_info=True)
   ```

## Integration Points

The logging system is integrated into:
- `webrotas/main.py` - Application lifecycle events
- `webrotas/routing_servers_interface.py` - Routing operations
- `webrotas/cache/bounding_boxes.py` - Cache operations

Additional modules can be easily integrated by importing `get_logger`:
```python
from webrotas.config.logging_config import get_logger
logger = get_logger(__name__)
```

## Future Enhancements

Potential improvements:
- JSON-formatted logs for structured analysis
- Remote log aggregation support
- Per-module log level configuration
- Request ID tracking for distributed tracing
- Performance metrics logging
