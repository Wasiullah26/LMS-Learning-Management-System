"""
Input validation utilities
"""

import re
from datetime import datetime


def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Args:
        password: Password string to validate
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None


def validate_role(role):
    """
    Validate user role
    
    Args:
        role: Role string to validate
    
    Returns:
        True if valid, False otherwise
    """
    return role in ['student', 'instructor']


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in data
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Returns:
        Tuple (is_valid, missing_fields)
    """
    missing = [field for field in required_fields if field not in data or data[field] is None]
    return len(missing) == 0, missing


def sanitize_string(value, max_length=None):
    """
    Sanitize string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string or None if invalid
    """
    if not isinstance(value, str):
        return None
    
    # Strip whitespace
    value = value.strip()
    
    # Check length
    if max_length and len(value) > max_length:
        return None
    
    # Return empty string as None
    if len(value) == 0:
        return None
    
    return value


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (e.g., {'pdf', 'jpg'})
    
    Returns:
        True if valid, False otherwise
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def validate_file_size(file_size, max_size):
    """
    Validate file size
    
    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes
    
    Returns:
        True if valid, False otherwise
    """
    return file_size <= max_size

