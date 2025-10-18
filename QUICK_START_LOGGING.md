# Quick Start Guide - webRotas Logging

## ⚡ 30-Second Setup

Add logging to any module in 3 lines:

```python
from webrotas.config.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Your message here")
```

## 📍 Log Levels

```python
logger.debug("Debug details (dev only, not shown in console)")
logger.info("Important info (shown in console)")
logger.warning("Warning (shown in console)")
logger.error("Error (shown in console)")
logger.critical("Critical (shown in console)")
```

## 📁 Where Are Logs?

```
webRotas/logs/
├── main.log
├── routing_servers_interface.log
└── bounding_boxes.log
```

Auto-created on first use. One file per module.

## 🎨 Console Output Examples

```
[INFO] webrotas.main - Server starting on port 5000
[WARNING] webrotas.main - Unknown argument detected
[ERROR] webrotas.cache.bounding_boxes - Failed to save cache
```

Colors automatically applied (if terminal supports it).

## 📝 File Output Examples

```
2025-10-18 02:38:30 - webrotas.main - INFO - [main.py:100] - Server starting
2025-10-18 02:38:31 - webrotas.cache.bounding_boxes - ERROR - [bounding_boxes.py:250] - Failed to save
```

Includes timestamp, module, level, and source location.

## 🧪 Test Logging

```bash
cd /home/ronaldo/Work/webRotas
uv run python src/test_logging.py
```

## ❌ DON'T

```python
# ❌ Wrong - old way (deprecated)
import logging
logger = logging.getLogger(__name__)

# ❌ Wrong - uses old wl module
from webrotas import wl
wl.wLog("message")

# ❌ Wrong - no logging at all
print("message")  # Use logger instead
```

## ✅ DO

```python
# ✅ Right - new way
from webrotas.config.logging_config import get_logger
logger = get_logger(__name__)

# Use appropriate levels
logger.debug("debug info")
logger.info("important event")
logger.warning("potential issue")
logger.error("operation failed", exc_info=True)
```

## 🔍 Debug with Full Traceback

```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

The `exc_info=True` adds full traceback to logs.

## 📊 Features

- ✅ Automatic file rotation (10 MB limit)
- ✅ Colored console output
- ✅ Detailed file format with timestamps
- ✅ No external dependencies
- ✅ Minimal performance overhead (~1ms)
- ✅ Thread-safe

## 🚀 Integration Status

Already integrated in:
- ✅ `webrotas/main.py` - Application startup
- ✅ `webrotas/routing_servers_interface.py` - Routing operations
- ✅ `webrotas/cache/bounding_boxes.py` - Cache management

## 📚 Full Documentation

- **`LOGGING.md`** - Complete guide with best practices
- **`LOGGING_IMPLEMENTATION_SUMMARY.md`** - Technical details
- **`RESUMO_LOGGING.md`** - Portuguese summary

## 🆘 Troubleshooting

### Logs not appearing in console
- This is normal for DEBUG level (console shows INFO+)
- Check file logs for DEBUG messages

### Logs directory not created
- First check if you have write permissions
- Try running `src/test_logging.py` to diagnose

### Old `wl` module errors
- Update imports to use `get_logger()`
- Search for `wl.` in your code and replace

## 💡 Pro Tips

1. **Use structured messages:**
   ```python
   logger.info(f"Processing route for region {region_id}")  # Good
   logger.info("Processing route")  # Less helpful
   ```

2. **Include context in errors:**
   ```python
   logger.error(f"Failed to load file {filepath}: {error}")
   ```

3. **Avoid sensitive data:**
   ```python
   logger.info(f"User login attempt for {username}")  # Good
   logger.info(f"User login with password: {password}")  # Bad!
   ```

## 📞 Need Help?

1. Check `LOGGING.md` section "Troubleshooting"
2. Run `src/test_logging.py` to verify setup
3. Check log files in `webRotas/logs/`
4. Look at existing usage in `main.py` or `routing_servers_interface.py`

---

**That's it!** You now have professional logging. Happy debugging! 🎉
