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
