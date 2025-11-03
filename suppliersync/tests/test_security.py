"""
Security tests for SupplierSync.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from core.security import (
    validate_path,
    validate_table_name,
    sanitize_filename,
    validate_sku,
    validate_price
)


class TestPathValidation:
    """Test path validation functions."""
    
    def test_path_traversal_blocked(self):
        """Test that path traversal attempts are blocked."""
        with pytest.raises(ValueError):
            validate_path("../../../etc/passwd", allow_absolute=False)
    
    def test_absolute_path_blocked(self):
        """Test that absolute paths are blocked when allow_absolute=False."""
        with pytest.raises(ValueError, match="Absolute paths"):
            validate_path("/etc/passwd", allow_absolute=False)
    
    def test_valid_relative_path(self):
        """Test that valid relative paths are allowed."""
        result = validate_path("data/docs", allow_absolute=False)
        assert result is not None
        # Result should be an absolute path
        assert os.path.isabs(result)
        assert "data" in result
    
    def test_path_within_base_dir(self):
        """Test that path validation respects base directory."""
        base_dir = os.getcwd()
        result = validate_path("data/docs", base_dir=base_dir, allow_absolute=False)
        assert result is not None
        assert os.path.isabs(result)
        assert base_dir in result
        
        # Path outside base directory should fail
        with pytest.raises(ValueError):
            validate_path("../../etc/passwd", base_dir=base_dir, allow_absolute=False)


class TestTableNameValidation:
    """Test table name validation."""
    
    def test_valid_table_name(self):
        """Test that valid table names pass validation."""
        allowed = ("products", "price_events", "supplier_updates")
        assert validate_table_name("products", allowed) is True
        assert validate_table_name("price_events", allowed) is True
    
    def test_invalid_table_name(self):
        """Test that invalid table names fail validation."""
        allowed = ("products", "price_events")
        assert validate_table_name("DROP TABLE", allowed) is False
        assert validate_table_name("'; DROP TABLE products; --", allowed) is False
        assert validate_table_name("unknown_table", allowed) is False


class TestFilenameSanitization:
    """Test filename sanitization."""
    
    def test_path_components_removed(self):
        """Test that path components are removed from filenames."""
        result = sanitize_filename("../../../etc/passwd")
        assert result == "passwd"
        assert "/" not in result
        assert ".." not in result
    
    def test_invalid_characters_removed(self):
        """Test that invalid characters are removed."""
        result = sanitize_filename("file<>:\"|?*.txt")
        assert result == "file.txt"
        assert "<" not in result
        assert ">" not in result
    
    def test_empty_filename(self):
        """Test that empty filenames raise error."""
        with pytest.raises(ValueError, match="Invalid filename"):
            sanitize_filename("")


class TestSKUValidation:
    """Test SKU validation."""
    
    def test_valid_sku(self):
        """Test that valid SKUs pass validation."""
        assert validate_sku("WF-001") is True
        assert validate_sku("PROD_123") is True
        assert validate_sku("SKU-ABC-123") is True
    
    def test_invalid_sku(self):
        """Test that invalid SKUs fail validation."""
        assert validate_sku("DROP TABLE products;") is False
        assert validate_sku("'; DELETE FROM products; --") is False
        assert validate_sku("") is False
        assert validate_sku("A" * 101) is False  # Too long


class TestPriceValidation:
    """Test price validation."""
    
    def test_valid_price(self):
        """Test that valid prices pass validation."""
        assert validate_price(0.0) is True
        assert validate_price(100.0) is True
        assert validate_price(1000.0) is True
    
    def test_invalid_price(self):
        """Test that invalid prices fail validation."""
        assert validate_price(-1.0) is False
        assert validate_price(2_000_000.0) is False  # Too high
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert validate_price(0) is True
        assert validate_price(1_000_000) is True  # Max allowed

