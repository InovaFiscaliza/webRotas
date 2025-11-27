"""Pydantic models for request validation"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Origin(BaseModel):
    """Origin/starting point for route"""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    description: str = Field(..., description="Location description")
    elevation: Optional[float] = Field(None, description="Elevation in meters")

    class Config:
        json_schema_extra = {
            "example": {
                "lat": -23.5505,
                "lng": -46.6333,
                "description": "São Paulo",
                "elevation": 760.0
            }
        }


class AvoidZone(BaseModel):
    """Geographic zone to avoid during routing"""
    name: str = Field(..., description="Zone name")
    coord: List[List[float]] = Field(
        ...,
        description="List of coordinates [latitude, longitude]"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Downtown",
                "coord": [[-23.55, -46.63], [-23.56, -46.64]]
            }
        }


class RouteRequest(BaseModel):
    """Base route request model"""
    type: str = Field(
        ...,
        description="Route type",
        pattern="^(shortest|circle|grid|ordered)$"
    )
    origin: Origin = Field(..., description="Starting point")
    parameters: Dict[str, Any] = Field(..., description="Route-type-specific parameters")
    avoidZones: Optional[List[AvoidZone]] = Field(
        default_factory=list,
        description="Zones to avoid"
    )
    criterion: Optional[str] = Field(
        default="distance",
        description="Routing criterion (distance, duration, or ordered)",
        pattern="^(distance|duration|ordered)$"
    )
    endpoint: Optional[Origin] = Field(
        default=None,
        description="Optional endpoint where route must end (must be one of the waypoints)"
    )
    closed: Optional[bool] = Field(
        default=False,
        description="If true, route returns to origin (closed tour). Cannot be true if endpoint is specified and differs from origin"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "shortest",
                "origin": {
                    "lat": -23.5505,
                    "lng": -46.6333,
                    "description": "Starting point"
                },
                "parameters": {
                    "waypoints": [{"lat": -23.55, "lng": -46.63}]
                },
                "avoidZones": [],
                "criterion": "distance"
            }
        }


class LogEntry(BaseModel):
    """Single log entry"""
    content: str = Field(..., description="Log line content")
    file: Optional[str] = Field(None, description="Log file name")
    timestamp: Optional[str] = Field(None, description="Log timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "[INFO] webrotas - Route processing completed",
                "file": "webrotas.log",
                "timestamp": "2024-11-24 20:23:32"
            }
        }


class LogResponse(BaseModel):
    """Response for log retrieval"""
    status: str = Field(..., description="Status of the request (success, error, warning)")
    logs: List[LogEntry] = Field(default_factory=list, description="Log entries")
    count: int = Field(..., description="Number of log entries returned")
    message: Optional[str] = Field(None, description="Additional message")
    limit: Optional[int] = Field(None, description="Limit applied to results")
    log_level_filter: Optional[str] = Field(None, description="Log level filter applied")
    module_filter: Optional[str] = Field(None, description="Module name filter applied")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "logs": [],
                "count": 0,
                "limit": 100
            }
        }


class ContainerLogResponse(BaseModel):
    """Response for container log retrieval"""
    status: str = Field(..., description="Status (success, error, warning)")
    container_name: Optional[str] = Field(None, description="Container name")
    logs: List[LogEntry] = Field(default_factory=list, description="Log entries")
    count: int = Field(..., description="Number of log entries")
    tail: Optional[int] = Field(None, description="Number of lines requested")
    cli_used: Optional[str] = Field(None, description="CLI tool used (podman or docker)")
    message: Optional[str] = Field(None, description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "container_name": "osrm",
                "logs": [],
                "count": 0,
                "tail": 100,
                "cli_used": "podman"
            }
        }


class LogFileInfo(BaseModel):
    """Information about a log file"""
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Absolute file path")
    size_bytes: int = Field(..., description="File size in bytes")
    size_mb: float = Field(..., description="File size in MB")
    modified: str = Field(..., description="Last modified timestamp")
    created: str = Field(..., description="Created timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "webrotas.log",
                "path": "/path/to/logs/webrotas.log",
                "size_bytes": 1024000,
                "size_mb": 1.0,
                "modified": "2024-11-24T20:23:32",
                "created": "2024-11-24T20:00:00"
            }
        }


class LogFilesResponse(BaseModel):
    """Response for log files listing"""
    status: str = Field(..., description="Status of the request")
    logs_directory: str = Field(..., description="Path to logs directory")
    files: List[LogFileInfo] = Field(default_factory=list, description="Log files")
    count: int = Field(..., description="Number of log files")
    directory_exists: bool = Field(..., description="Whether logs directory exists")
    message: Optional[str] = Field(None, description="Additional message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "logs_directory": "/path/to/logs",
                "files": [],
                "count": 0,
                "directory_exists": True
            }
        }


class CombinedLogsResponse(BaseModel):
    """Response combining application and container logs"""
    status: str = Field(..., description="Status of the request")
    timestamp: str = Field(..., description="Response timestamp")
    app_logs: LogResponse = Field(..., description="Application logs")
    container_logs: ContainerLogResponse = Field(..., description="Container logs")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-11-24T20:23:32",
                "app_logs": {"status": "success", "logs": [], "count": 0},
                "container_logs": {"status": "success", "logs": [], "count": 0, "container_name": "osrm"}
            }
        }
