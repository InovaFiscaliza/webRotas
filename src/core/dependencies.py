"""Dependency injection utilities for FastAPI"""

from typing import Any, Dict
from fastapi import Query

from config.constants import KEYS_ROOT, KEYS_PARAMETERS, VALID_REQUEST_TYPES
from core.exceptions import (
    MissingSessionIdError,
    MissingRequiredFieldsError,
    InvalidRequestTypeError,
    InvalidParametersError,
    MissingParametersError,
)


async def validate_session_id(session_id: str = Query(...)) -> str:
    """Validate that sessionId is provided via query parameter"""
    if not session_id:
        raise MissingSessionIdError()
    return session_id


async def validate_request_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the basic structure of the request"""
    if not data:
        raise MissingRequiredFieldsError(KEYS_ROOT["required"])
    
    missing_fields = KEYS_ROOT["required"] - data.keys()
    if missing_fields:
        raise MissingRequiredFieldsError(missing_fields)
    
    return data


async def validate_request_type(request_type: str) -> str:
    """Validate that the request type is valid"""
    if not request_type or request_type not in VALID_REQUEST_TYPES:
        raise InvalidRequestTypeError(request_type)
    return request_type


async def validate_parameters(
    request_type: str,
    parameters: Any
) -> Dict[str, Any]:
    """Validate that parameters field is a dict and contains required keys"""
    if not isinstance(parameters, dict):
        raise InvalidParametersError()
    
    required_params = KEYS_PARAMETERS.get(request_type, set())
    missing_params = required_params - parameters.keys()
    
    if missing_params:
        raise MissingParametersError(request_type, missing_params)
    
    return parameters
