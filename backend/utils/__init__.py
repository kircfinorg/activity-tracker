"""Utility modules for the backend"""

from .firebase_error_handler import (
    get_firebase_error_message,
    is_network_error,
    is_permission_error,
    is_data_corruption_error,
    retry_operation,
    with_retry,
    validate_document_data,
    safe_get_field,
    RetryConfig,
    FirebaseErrorHandler,
)

__all__ = [
    'get_firebase_error_message',
    'is_network_error',
    'is_permission_error',
    'is_data_corruption_error',
    'retry_operation',
    'with_retry',
    'validate_document_data',
    'safe_get_field',
    'RetryConfig',
    'FirebaseErrorHandler',
]
