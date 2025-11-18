"""Backwards compatibility shim - imports moved to infrastructure/routing/matrix_builder.py"""

from webrotas.infrastructure.routing.matrix_builder import (
    IterativeMatrixBuilder,
    RequestBatch,
    PUBLIC_API_BATCH_SIZE,
    PUBLIC_API_MAX_RETRIES,
    PUBLIC_API_RETRY_BASE_DELAY,
    PUBLIC_API_RATE_LIMIT_DELAY,
    TIMEOUT,
    URL_TABLE,
)

__all__ = [
    "IterativeMatrixBuilder",
    "RequestBatch",
    "PUBLIC_API_BATCH_SIZE",
    "PUBLIC_API_MAX_RETRIES",
    "PUBLIC_API_RETRY_BASE_DELAY",
    "PUBLIC_API_RATE_LIMIT_DELAY",
    "TIMEOUT",
    "URL_TABLE",
]
