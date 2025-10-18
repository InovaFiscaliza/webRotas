"""Custom exceptions for webRotas API"""

from fastapi import HTTPException, status


class WebRotasException(Exception):
    """Base exception for webRotas"""
    pass


class InvalidRequestError(HTTPException):
    """Raised when request validation fails"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class MissingSessionIdError(InvalidRequestError):
    """Raised when sessionId is missing"""
    def __init__(self):
        super().__init__(
            detail="Invalid or missing sessionId",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class InvalidRequestTypeError(InvalidRequestError):
    """Raised when request type is invalid"""
    def __init__(self, request_type: str = None):
        if request_type:
            detail = f"Invalid or missing request type: '{request_type}'"
        else:
            detail = "Invalid or missing request type"
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class MissingRequiredFieldsError(InvalidRequestError):
    """Raised when required fields are missing"""
    def __init__(self, missing_fields: set):
        detail = f"Invalid or missing JSON payload. Required fields: {sorted(list(missing_fields))}"
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class MissingParametersError(InvalidRequestError):
    """Raised when required parameters are missing"""
    def __init__(self, request_type: str, missing_params: set):
        detail = f"Missing required parameters for type '{request_type}': {sorted(list(missing_params))}"
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidParametersError(InvalidRequestError):
    """Raised when parameters are not a dict"""
    def __init__(self):
        super().__init__(
            detail="Parameters field must be a JSON object",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ProcessingError(HTTPException):
    """Raised when route processing fails"""
    def __init__(self, error_message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {error_message}"
        )
