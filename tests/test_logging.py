#!/usr/bin/env python3
"""
Test script to verify logging configuration is working properly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from webrotas.config.logging_config import get_logger
from webrotas.config.constants import LOGS_PATH


def test_logging():
    """Test logging functionality."""

    print("=" * 60)
    print("Testing webRotas Logging Configuration")
    print("=" * 60)

    # Create loggers for different modules
    logger_main = get_logger("webrotas.main")
    logger_routing = get_logger("webrotas.routing_servers_interface")
    logger_cache = get_logger("webrotas.cache.bounding_boxes")

    # Test logging at different levels
    print("\n[TEST] Logging messages at different levels...\n")

    logger_main.debug("This is a DEBUG message from main module")
    logger_main.info("This is an INFO message from main module")
    logger_main.warning("This is a WARNING message from main module")
    logger_main.error("This is an ERROR message from main module")

    logger_routing.debug("This is a DEBUG message from routing module")
    logger_routing.info("This is an INFO message from routing module")

    logger_cache.debug("This is a DEBUG message from cache module")
    logger_cache.info("This is an INFO message from cache module")

    # Check if log files were created
    print("\n[TEST] Checking log files...\n")

    LOGS_PATH.mkdir(parents=True, exist_ok=True)
    log_files = list(LOGS_PATH.glob("*.log"))

    if log_files:
        print(f"✓ Log directory exists: {LOGS_PATH}")
        print(f"✓ Found {len(log_files)} log file(s):")
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"  - {log_file.name} ({size} bytes)")
    else:
        print(f"⚠ No log files found in {LOGS_PATH}")

    print("\n" + "=" * 60)
    print("Logging test completed successfully!")
    print("=" * 60)

    return len(log_files) > 0


if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1)
