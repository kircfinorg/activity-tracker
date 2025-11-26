"""
Firebase Error Handling Utilities

Provides error handling, retry logic, and user-friendly error messages
for Firebase operations.

Validates: Requirements 14.4, 14.5 - Handle connection errors and corrupted data
"""

import logging
import time
from typing import Callable, TypeVar, Any, Optional
from functools import wraps
from firebase_admin import exceptions

logger = logging.getLogger(__name__)

T = TypeVar('T')

# User-friendly error messages for common Firebase errors
ERROR_MESSAGES = {
    'PERMISSION_DENIED': 'You do not have permission to access this data.',
    'NOT_FOUND': 'The requested data was not found.',
    'ALREADY_EXISTS': 'This data already exists.',
    'RESOURCE_EXHAUSTED': 'Too many requests. Please try again later.',
    'FAILED_PRECONDITION': 'Operation cannot be performed in the current state.',
    'ABORTED': 'Operation was aborted. Please try again.',
    'OUT_OF_RANGE': 'Operation was attempted past the valid range.',
    'UNIMPLEMENTED': 'This operation is not implemented.',
    'INTERNAL': 'An internal error occurred. Please try again.',
    'UNAVAILABLE': 'Service is currently unavailable. Please check your connection.',
    'DATA_LOSS': 'Data loss or corruption detected.',
    'UNAUTHENTICATED': 'You must be signed in to perform this action.',
    'DEADLINE_EXCEEDED': 'Operation timed out. Please try again.',
    'CANCELLED': 'Operation was cancelled.',
    'INVALID_ARGUMENT': 'Invalid data provided.',
    'UNKNOWN': 'An unknown error occurred.',
}


def get_firebase_error_message(error: Exception) -> str:
    """
    Get user-friendly error message from Firebase error
    
    Args:
        error: The exception to get message for
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, exceptions.FirebaseError):
        code = error.code if hasattr(error, 'code') else 'UNKNOWN'
        return ERROR_MESSAGES.get(code, str(error))
    
    return str(error)


def is_network_error(error: Exception) -> bool:
    """
    Check if error is a network/connection error
    
    Args:
        error: The exception to check
        
    Returns:
        True if network error, False otherwise
    """
    if isinstance(error, exceptions.FirebaseError):
        code = error.code if hasattr(error, 'code') else ''
        return code in ['UNAVAILABLE', 'DEADLINE_EXCEEDED', 'CANCELLED']
    
    return False


def is_permission_error(error: Exception) -> bool:
    """
    Check if error is a permission error
    
    Args:
        error: The exception to check
        
    Returns:
        True if permission error, False otherwise
    """
    if isinstance(error, exceptions.FirebaseError):
        code = error.code if hasattr(error, 'code') else ''
        return code in ['PERMISSION_DENIED', 'UNAUTHENTICATED']
    
    return False


def is_data_corruption_error(error: Exception) -> bool:
    """
    Check if error indicates corrupted data
    
    Args:
        error: The exception to check
        
    Returns:
        True if data corruption error, False otherwise
    """
    if isinstance(error, exceptions.FirebaseError):
        code = error.code if hasattr(error, 'code') else ''
        return code in ['DATA_LOSS', 'INVALID_ARGUMENT']
    
    return False


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_multiplier: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier


def retry_operation(
    operation: Callable[[], T],
    config: Optional[RetryConfig] = None
) -> T:
    """
    Retry a Firebase operation with exponential backoff
    
    Args:
        operation: The operation to retry
        config: Retry configuration
        
    Returns:
        Result of the operation
        
    Raises:
        Exception: If all retry attempts fail
    """
    if config is None:
        config = RetryConfig()
    
    last_error: Optional[Exception] = None
    delay = config.initial_delay
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            return operation()
        except Exception as error:
            last_error = error
            
            # Don't retry permission errors or data corruption errors
            if is_permission_error(error) or is_data_corruption_error(error):
                raise
            
            # Only retry network errors
            if not is_network_error(error):
                raise
            
            # Don't retry on last attempt
            if attempt == config.max_attempts:
                break
            
            logger.warning(
                f"Firebase operation failed (attempt {attempt}/{config.max_attempts}). "
                f"Retrying in {delay}s...",
                exc_info=error
            )
            
            time.sleep(delay)
            delay = min(delay * config.backoff_multiplier, config.max_delay)
    
    raise last_error


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator to add retry logic to a function
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return retry_operation(
                lambda: func(*args, **kwargs),
                config
            )
        return wrapper
    return decorator


def validate_document_data(data: dict, required_fields: list[str]) -> bool:
    """
    Validate Firestore document data
    
    Checks for required fields and data integrity
    
    Args:
        data: Document data to validate
        required_fields: List of required field names
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If data is invalid or missing required fields
    """
    if not isinstance(data, dict):
        raise ValueError('Invalid document data: data must be a dictionary')
    
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValueError(
            f"Corrupted data: missing required fields: {', '.join(missing_fields)}"
        )
    
    return True


def safe_get_field(data: dict, field: str, default: Any = None) -> Any:
    """
    Safe document data getter with validation
    
    Args:
        data: Document data
        field: Field name to get
        default: Default value if field is missing
        
    Returns:
        Field value or default
    """
    if not isinstance(data, dict):
        logger.warning(f"Invalid document data when accessing field: {field}")
        return default
    
    if field not in data:
        logger.warning(f"Missing field in document: {field}")
        return default
    
    return data[field]


class FirebaseErrorHandler:
    """
    Context manager for handling Firebase errors
    
    Usage:
        with FirebaseErrorHandler("fetch user data"):
            user_doc = db.collection('users').document(user_id).get()
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True
        
        if isinstance(exc_val, exceptions.FirebaseError):
            logger.error(
                f"Firebase error during {self.operation_name}: {get_firebase_error_message(exc_val)}",
                exc_info=exc_val
            )
        else:
            logger.error(
                f"Error during {self.operation_name}: {str(exc_val)}",
                exc_info=exc_val
            )
        
        # Don't suppress the exception
        return False
