"""
Centralized Error Handling Utilities

Provides consistent HTTP status codes and error responses across the API.

Validates: Requirements 15.4, 15.5 - HTTP status codes and error messages
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import traceback
import uuid

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base class for API errors with status code and detail"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.extra = extra or {}
        super().__init__(detail)


class BadRequestError(APIError):
    """400 Bad Request error"""
    
    def __init__(self, detail: str, error_code: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, error_code, extra)


class UnauthorizedError(APIError):
    """401 Unauthorized error"""
    
    def __init__(self, detail: str = "Authentication required", error_code: Optional[str] = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, error_code)


class ForbiddenError(APIError):
    """403 Forbidden error"""
    
    def __init__(self, detail: str = "Access denied", error_code: Optional[str] = None):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, error_code)


class NotFoundError(APIError):
    """404 Not Found error"""
    
    def __init__(self, detail: str, error_code: Optional[str] = None):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, error_code)


class ConflictError(APIError):
    """409 Conflict error"""
    
    def __init__(self, detail: str, error_code: Optional[str] = None):
        super().__init__(status.HTTP_409_CONFLICT, detail, error_code)


class InternalServerError(APIError):
    """500 Internal Server Error"""
    
    def __init__(self, detail: str = "Internal server error", error_code: Optional[str] = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, error_code)


def log_error(
    error: Exception,
    request: Optional[Request] = None,
    user_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Log error with detailed context
    
    Validates: Requirements 15.5 - Log errors with details
    
    Args:
        error: The exception that occurred
        request: Optional FastAPI request object
        user_id: Optional user ID for context
        extra_context: Optional additional context
        
    Returns:
        Error ID for tracking
    """
    error_id = str(uuid.uuid4())
    
    context = {
        'error_id': error_id,
        'error_type': type(error).__name__,
        'error_message': str(error),
    }
    
    if user_id:
        context['user_id'] = user_id
    
    if request:
        context['method'] = request.method
        context['url'] = str(request.url)
        context['client_host'] = request.client.host if request.client else None
    
    if extra_context:
        context.update(extra_context)
    
    # Log with full traceback for debugging
    logger.error(
        f"Error {error_id}: {type(error).__name__} - {str(error)}",
        extra=context,
        exc_info=True
    )
    
    return error_id


def create_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    error_id: Optional[str] = None,
    details: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Validates: Requirements 15.4, 15.5 - Appropriate status codes and descriptive messages
    
    Args:
        status_code: HTTP status code
        message: Error message
        error_code: Optional error code for client handling
        error_id: Optional error ID for tracking
        details: Optional additional error details
        
    Returns:
        Error response dictionary
    """
    response = {
        'error': True,
        'status_code': status_code,
        'message': message
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if error_id:
        response['error_id'] = error_id
    
    if details:
        response['details'] = details
    
    return response


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handler for custom API errors
    
    Args:
        request: FastAPI request
        exc: APIError exception
        
    Returns:
        JSON response with error details
    """
    error_id = log_error(exc, request)
    
    response = create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=exc.error_code,
        error_id=error_id,
        details=exc.extra if exc.extra else None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for FastAPI HTTPException
    
    Args:
        request: FastAPI request
        exc: HTTPException
        
    Returns:
        JSON response with error details
    """
    error_id = log_error(exc, request)
    
    response = create_error_response(
        status_code=exc.status_code,
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        error_id=error_id,
        details=exc.detail if not isinstance(exc.detail, str) else None
    )
    
    # Add 'detail' field for backward compatibility with existing tests
    response['detail'] = exc.detail
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors
    
    Args:
        request: FastAPI request
        exc: RequestValidationError
        
    Returns:
        JSON response with validation error details
    """
    error_id = log_error(exc, request)
    
    # Format validation errors
    errors = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'])
        errors.append({
            'field': field,
            'message': error['msg'],
            'type': error['type']
        })
    
    response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation failed",
        error_code="VALIDATION_ERROR",
        error_id=error_id,
        details={'errors': errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unexpected exceptions
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON response with generic error message
    """
    error_id = log_error(exc, request)
    
    # Don't expose internal error details to clients
    response = create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please try again later.",
        error_code="INTERNAL_ERROR",
        error_id=error_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response
    )


def get_status_code_for_operation(operation_result: str) -> int:
    """
    Get appropriate HTTP status code for operation result
    
    Validates: Requirements 15.4 - Return appropriate HTTP status codes
    
    Args:
        operation_result: String describing the operation result
        
    Returns:
        HTTP status code
    """
    status_map = {
        'created': status.HTTP_201_CREATED,
        'success': status.HTTP_200_OK,
        'updated': status.HTTP_200_OK,
        'deleted': status.HTTP_200_OK,
        'no_content': status.HTTP_204_NO_CONTENT,
        'bad_request': status.HTTP_400_BAD_REQUEST,
        'unauthorized': status.HTTP_401_UNAUTHORIZED,
        'forbidden': status.HTTP_403_FORBIDDEN,
        'not_found': status.HTTP_404_NOT_FOUND,
        'conflict': status.HTTP_409_CONFLICT,
        'validation_error': status.HTTP_422_UNPROCESSABLE_ENTITY,
        'server_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    return status_map.get(operation_result.lower(), status.HTTP_200_OK)
