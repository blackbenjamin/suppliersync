"""
Security utilities for SupplierSync.

This module provides security helpers for input validation, path sanitization,
and other security-related functions.
"""

import os
import re
from pathlib import Path
from typing import Optional


def validate_path(path: str, base_dir: Optional[str] = None, allow_absolute: bool = False) -> str:
    """
    Validate and sanitize file paths to prevent path traversal attacks.
    
    Args:
        path: Path to validate
        base_dir: Base directory to restrict paths to (optional)
        allow_absolute: Whether to allow absolute paths (default: False)
    
    Returns:
        Normalized, validated path (always absolute)
    
    Raises:
        ValueError: If path is invalid or attempts path traversal
    """
    # Check for absolute paths in input (before normalization)
    if not allow_absolute and os.path.isabs(path):
        raise ValueError("Absolute paths not allowed")
    
    # Check for path traversal attempts in input
    if ".." in path or "//" in path:
        raise ValueError("Path traversal detected")
    
    # Resolve symlinks and normalize path (convert to absolute for normalization)
    try:
        resolved = os.path.realpath(os.path.abspath(path))
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")
    
    # If base_dir is specified, ensure path is within it
    if base_dir:
        base_resolved = os.path.realpath(os.path.abspath(base_dir))
        try:
            # Check if resolved path is within base directory
            Path(resolved).relative_to(Path(base_resolved))
        except ValueError:
            raise ValueError(f"Path must be within {base_dir}")
    
    return resolved


def validate_table_name(table_name: str, allowed_tables: tuple) -> bool:
    """
    Validate table name against whitelist to prevent SQL injection.
    
    Args:
        table_name: Table name to validate
        allowed_tables: Tuple of allowed table names
    
    Returns:
        True if valid, False otherwise
    """
    return table_name in allowed_tables


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and invalid characters.
    
    Args:
        filename: Filename to sanitize
    
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        raise ValueError("Invalid filename")
    
    return filename


def validate_sku(sku: str) -> bool:
    """
    Validate SKU format to prevent injection attacks.
    
    Args:
        sku: SKU to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Allow alphanumeric, hyphens, and underscores
    # Adjust pattern based on your SKU format requirements
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, sku)) and len(sku) <= 100


def validate_price(price: float) -> bool:
    """
    Validate price value to prevent injection attacks.
    
    Args:
        price: Price to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Price must be positive and reasonable
    return 0 <= price <= 1_000_000  # Adjust max as needed

