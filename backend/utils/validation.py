"""
Input Validation Utilities

Provides comprehensive input validation and sanitization for API requests.

Validates: Requirements 17.1, 17.2, 17.3 - Input validation, error messages, and sanitization
"""

import re
import logging
from typing import Any, Optional
from pydantic import ValidationError
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Validation patterns
ALPHANUMERIC_PATTERN = re.compile(r'^[A-Za-z0-9]+$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
INVITE_CODE_PATTERN = re.compile(r'^[A-Z0-9]{6}$')

# Dangerous patterns for injection attacks
DANGEROUS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers like onclick=
    re.compile(r'<iframe', re.IGNORECASE),
    re.compile(r'<object', re.IGNORECASE),
    re.compile(r'<embed', re.IGNORECASE),
]


def handle_validation_error(error: ValidationError) -> HTTPException:
    """
    Convert Pydantic ValidationError to HTTPException with detailed messages
    
    Validates: Requirements 17.2 - Return specific validation error messages
    
    Args:
        error: Pydantic ValidationError
        
    Returns:
        HTTPException with detailed error information
    """
    errors = []
    for err in error.errors():
        field = '.'.join(str(loc) for loc in err['loc'])
        message = err['msg']
        error_type = err['type']
        
        # Create user-friendly error message
        if error_type == 'value_error.missing':
            errors.append(f"{field}: This field is required")
        elif error_type == 'type_error.integer':
            errors.append(f"{field}: Must be an integer")
        elif error_type == 'type_error.float':
            errors.append(f"{field}: Must be a number")
        elif error_type == 'value_error.any_str.min_length':
            errors.append(f"{field}: Must not be empty")
        elif 'greater_than' in error_type:
            errors.append(f"{field}: Must be greater than 0")
        else:
            errors.append(f"{field}: {message}")
    
    logger.warning(f"Validation error: {'; '.join(errors)}")
    
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Validation failed",
            "errors": errors
        }
    )


def validate_string_not_empty(value: str, field_name: str) -> str:
    """
    Validate that a string is not empty or only whitespace
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Stripped string value
        
    Raises:
        ValueError: If string is empty or only whitespace
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty or only whitespace")
    return value.strip()


def validate_positive_number(value: float, field_name: str) -> float:
    """
    Validate that a number is positive
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        value: Number value to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated number
        
    Raises:
        ValueError: If number is not positive
    """
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive value")
    return value


def validate_invite_code(code: str) -> str:
    """
    Validate invite code format
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        code: Invite code to validate
        
    Returns:
        Uppercase invite code
        
    Raises:
        ValueError: If code format is invalid
    """
    code = code.strip().upper()
    
    if not INVITE_CODE_PATTERN.match(code):
        raise ValueError("Invalid invite code format - must be exactly 6 alphanumeric characters")
    
    return code


def validate_role(role: str) -> str:
    """
    Validate user role
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        role: Role to validate
        
    Returns:
        The validated role
        
    Raises:
        ValueError: If role is invalid
    """
    valid_roles = ['parent', 'child']
    
    if role not in valid_roles:
        raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
    
    return role


def validate_verification_status(status_value: str) -> str:
    """
    Validate verification status
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        status_value: Status to validate
        
    Returns:
        The validated status
        
    Raises:
        ValueError: If status is invalid
    """
    valid_statuses = ['pending', 'approved', 'rejected']
    
    if status_value not in valid_statuses:
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
    
    return status_value


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input to prevent injection attacks
    
    Validates: Requirements 17.3 - Sanitize all string inputs to prevent injection attacks
    
    Args:
        value: String to sanitize
        max_length: Optional maximum length to enforce
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove any dangerous patterns
    sanitized = value
    for pattern in DANGEROUS_PATTERNS:
        sanitized = pattern.sub('', sanitized)
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Trim to max length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def sanitize_activity_name(name: str) -> str:
    """
    Sanitize activity name
    
    Validates: Requirements 17.3 - Sanitize string inputs
    
    Args:
        name: Activity name to sanitize
        
    Returns:
        Sanitized activity name
    """
    return sanitize_string(name, max_length=100)


def sanitize_unit_name(unit: str) -> str:
    """
    Sanitize unit name
    
    Validates: Requirements 17.3 - Sanitize string inputs
    
    Args:
        unit: Unit name to sanitize
        
    Returns:
        Sanitized unit name
    """
    return sanitize_string(unit, max_length=50)


def validate_and_sanitize_activity_data(name: str, unit: str, rate: float) -> tuple[str, str, float]:
    """
    Validate and sanitize activity creation data
    
    Validates: Requirements 17.1, 17.3 - Validate and sanitize inputs
    
    Args:
        name: Activity name
        unit: Unit name
        rate: Rate value
        
    Returns:
        Tuple of (sanitized_name, sanitized_unit, validated_rate)
        
    Raises:
        ValueError: If validation fails
    """
    # Sanitize strings
    sanitized_name = sanitize_activity_name(name)
    sanitized_unit = sanitize_unit_name(unit)
    
    # Validate not empty after sanitization
    validate_string_not_empty(sanitized_name, "Activity name")
    validate_string_not_empty(sanitized_unit, "Unit")
    
    # Validate rate
    validate_positive_number(rate, "Rate")
    
    return sanitized_name, sanitized_unit, rate


def validate_id_format(id_value: str, field_name: str) -> str:
    """
    Validate ID format (basic validation)
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        id_value: ID to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated ID
        
    Raises:
        ValueError: If ID format is invalid
    """
    if not id_value or not id_value.strip():
        raise ValueError(f"{field_name} must not be empty")
    
    # Basic validation - IDs should be alphanumeric with possible hyphens/underscores
    if not re.match(r'^[A-Za-z0-9_-]+$', id_value):
        raise ValueError(f"{field_name} contains invalid characters")
    
    return id_value.strip()


def validate_units(units: int) -> int:
    """
    Validate units value
    
    Validates: Requirements 17.1 - Validate all fields against expected formats
    
    Args:
        units: Units value to validate
        
    Returns:
        The validated units
        
    Raises:
        ValueError: If units is not positive
    """
    if units <= 0:
        raise ValueError("Units must be a positive integer")
    
    return units
