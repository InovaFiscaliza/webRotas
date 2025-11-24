"""
Service for retrieving and managing application and container logs.

Provides functionality to:
- Read application log files from the logs directory
- Fetch container logs via Docker API
- Format and combine logs from multiple sources
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from webrotas.config.constants import LOGS_PATH
from webrotas.config.logging_config import get_logger
from webrotas.infrastructure.docker import (
    get_docker_client,
    ContainerNotFoundError,
    DockerClientError,
)

logger = get_logger(__name__)


def get_app_logs(
    limit: int = 100,
    log_level: Optional[str] = None,
    module_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve application logs from log files.

    Args:
        limit: Maximum number of log lines to return
        log_level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        module_name: Filter by module name pattern

    Returns:
        Dictionary containing logs and metadata
    """
    try:
        logs = []
        log_files = []

        # Get all log files from logs directory
        if LOGS_PATH.exists():
            log_files = sorted(
                LOGS_PATH.glob("*.log*"), key=lambda x: x.stat().st_mtime, reverse=True
            )

        if not log_files:
            return {
                "status": "success",
                "logs": [],
                "count": 0,
                "message": "No log files found",
            }

        # Read logs from most recent files
        total_lines = 0
        for log_file in log_files:
            if total_lines >= limit:
                break

            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                    # Process lines in reverse order (most recent first)
                    for line in reversed(lines):
                        if total_lines >= limit:
                            break

                        # Apply filters
                        if (
                            log_level
                            and f"[{log_level}]" not in line
                            and log_level not in line
                        ):
                            continue
                        if module_name and module_name not in line:
                            continue

                        logs.append(
                            {
                                "file": log_file.name,
                                "content": line.rstrip(),
                                "timestamp": _extract_timestamp(line),
                            }
                        )
                        total_lines += 1

            except Exception as e:
                logger.warning(f"Error reading log file {log_file}: {e}")
                continue

        # Reverse to show chronological order (oldest first in result)
        logs.reverse()

        return {
            "status": "success",
            "logs": logs,
            "count": len(logs),
            "limit": limit,
            "log_level_filter": log_level,
            "module_filter": module_name,
        }

    except Exception as e:
        logger.error(f"Error retrieving application logs: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "logs": []}


def get_container_logs(
    container_name: str = "osrm",
    tail: int = 100,
) -> Dict[str, Any]:
    """
    Retrieve container logs using Docker API.

    Args:
        container_name: Name of the container (default: 'osrm')
        tail: Number of most recent log lines to return

    Returns:
        Dictionary containing container logs and status
    """
    try:
        docker_client = get_docker_client()
        
        # Try to get logs from the container
        logs = docker_client.get_container_logs(container_name, tail=tail)
        
        # Parse log lines
        log_lines = [
            {"content": line.rstrip()} for line in logs.split("\n") if line.strip()
        ]
        
        return {
            "status": "success",
            "container_name": container_name,
            "logs": log_lines,
            "count": len(log_lines),
            "tail": tail,
        }
    
    except ContainerNotFoundError:
        logger.warning(f"Container '{container_name}' not found")
        return {
            "status": "warning",
            "message": f"Container '{container_name}' not found. Ensure the container is running.",
            "container_name": container_name,
            "logs": [],
            "tail": tail,
        }
    
    except DockerClientError as e:
        logger.error(f"Docker client error: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve container logs: {str(e)}",
            "container_name": container_name,
            "logs": [],
        }
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving container logs: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "container_name": container_name,
            "logs": [],
        }


def get_combined_logs(
    app_limit: int = 50,
    container_tail: int = 50,
    container_name: str = "osrm",
) -> Dict[str, Any]:
    """
    Retrieve both application and container logs in a unified response.

    Args:
        app_limit: Maximum number of application log lines
        container_tail: Maximum number of container log lines
        container_name: Name of the container

    Returns:
        Dictionary containing both app and container logs
    """
    app_logs = get_app_logs(limit=app_limit)
    container_logs = get_container_logs(
        container_name=container_name, tail=container_tail
    )

    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "app_logs": app_logs,
        "container_logs": container_logs,
    }


def get_log_files_info() -> Dict[str, Any]:
    """
    Get information about available log files.

    Returns:
        Dictionary containing log files and their details
    """
    try:
        files_info = []

        if LOGS_PATH.exists():
            for log_file in sorted(LOGS_PATH.glob("*.log*")):
                try:
                    stat = log_file.stat()
                    files_info.append(
                        {
                            "name": log_file.name,
                            "path": str(log_file),
                            "size_bytes": stat.st_size,
                            "size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "created": datetime.fromtimestamp(
                                stat.st_ctime
                            ).isoformat(),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Error getting info for {log_file}: {e}")
                    continue

        return {
            "status": "success",
            "logs_directory": str(LOGS_PATH),
            "files": files_info,
            "count": len(files_info),
            "directory_exists": LOGS_PATH.exists(),
        }

    except Exception as e:
        logger.error(f"Error retrieving log files info: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "files": []}


def _extract_timestamp(log_line: str) -> Optional[str]:
    """
    Extract timestamp from a log line.

    Expected format: "YYYY-MM-DD HH:MM:SS"

    Args:
        log_line: Log line to parse

    Returns:
        Extracted timestamp or None
    """
    try:
        # Try to find ISO format timestamp
        if len(log_line) > 19:
            potential_timestamp = log_line[:19]
            # Simple validation: check if it matches YYYY-MM-DD HH:MM:SS format
            if (
                len(potential_timestamp) == 19
                and potential_timestamp[4] == "-"
                and potential_timestamp[7] == "-"
                and potential_timestamp[10] == " "
                and potential_timestamp[13] == ":"
                and potential_timestamp[16] == ":"
            ):
                return potential_timestamp
    except Exception:
        pass

    return None
