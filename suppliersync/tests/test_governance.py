"""
Pytest tests for governance logic.
Run with: pytest tests/test_governance.py
Or from suppliersync directory: python -m pytest tests/test_governance.py
"""

import sys
from pathlib import Path

# Add suppliersync directory to path if not already there
suppliersync_dir = Path(__file__).parent.parent
if str(suppliersync_dir) not in sys.path:
    sys.path.insert(0, str(suppliersync_dir))

import pytest
from datetime import datetime, timedelta
from core.governance import enforce_policy


def test_retail_below_wholesale():
    """Test that retail price below wholesale is rejected."""
    price_changes = [{"sku": "TEST-001", "new_price": 50.0}]
    sku_to_wholesale = {"TEST-001": 100.0}
    
    approved, rejected = enforce_policy(price_changes, sku_to_wholesale)
    
    assert len(approved) == 0
    assert len(rejected) == 1
    assert rejected[0]["reject_reason"] == "retail_below_wholesale"


def test_margin_below_minimum():
    """Test that prices with margin below 5% are rejected."""
    price_changes = [{"sku": "TEST-002", "new_price": 104.0}]
    sku_to_wholesale = {"TEST-002": 100.0}  # 4% margin (below 5% minimum)
    
    approved, rejected = enforce_policy(price_changes, sku_to_wholesale)
    
    assert len(approved) == 0
    assert len(rejected) == 1
    assert rejected[0]["reject_reason"] == "margin_below_minimum"


def test_valid_price_approved():
    """Test that valid prices are approved."""
    price_changes = [{"sku": "TEST-003", "new_price": 150.0}]
    sku_to_wholesale = {"TEST-003": 100.0}  # 50% margin
    
    approved, rejected = enforce_policy(price_changes, sku_to_wholesale)
    
    assert len(approved) == 1
    assert len(rejected) == 0
    assert approved[0]["sku"] == "TEST-003"


def test_daily_drift_exceeded():
    """Test that daily price changes >20% are rejected."""
    today = datetime.now()
    price_changes = [{"sku": "TEST-004", "new_price": 150.0}]
    sku_to_wholesale = {"TEST-004": 100.0}
    sku_to_current_price = {"TEST-004": 100.0}
    sku_to_last_price_date = {"TEST-004": today}
    
    approved, rejected = enforce_policy(
        price_changes,
        sku_to_wholesale,
        sku_to_current_price=sku_to_current_price,
        sku_to_last_price_date=sku_to_last_price_date,
    )
    
    assert len(approved) == 0
    assert len(rejected) == 1
    assert rejected[0]["reject_reason"] == "daily_drift_exceeded"


def test_daily_drift_within_limit():
    """Test that daily price changes <=20% are approved."""
    today = datetime.now()
    price_changes = [{"sku": "TEST-005", "new_price": 115.0}]
    sku_to_wholesale = {"TEST-005": 100.0}
    sku_to_current_price = {"TEST-005": 100.0}
    sku_to_last_price_date = {"TEST-005": today}
    
    approved, rejected = enforce_policy(
        price_changes,
        sku_to_wholesale,
        sku_to_current_price=sku_to_current_price,
        sku_to_last_price_date=sku_to_last_price_date,
    )
    
    assert len(approved) == 1
    assert len(rejected) == 0


def test_category_blocked(monkeypatch):
    """Test that blocked categories are rejected."""
    # Set BLOCKED_CATEGORIES via monkeypatch
    monkeypatch.setenv("BLOCKED_CATEGORIES", "restricted")
    
    # Re-import to pick up new env var
    import importlib
    from core import governance
    importlib.reload(governance)
    from core.governance import enforce_policy
    
    price_changes = [{"sku": "TEST-006", "new_price": 150.0}]
    sku_to_wholesale = {"TEST-006": 100.0}
    sku_to_category = {"TEST-006": "restricted"}
    
    approved, rejected = enforce_policy(
        price_changes,
        sku_to_wholesale,
        sku_to_category=sku_to_category,
    )
    
    assert len(approved) == 0
    assert len(rejected) == 1
    assert rejected[0]["reject_reason"] == "category_blocked"


def test_missing_sku():
    """Test that missing SKU is rejected."""
    price_changes = [{"new_price": 150.0}]  # No SKU
    
    approved, rejected = enforce_policy(price_changes, {})
    
    assert len(approved) == 0
    assert len(rejected) == 1
    assert rejected[0]["reject_reason"] == "missing_sku"


def test_invalid_price_format():
    """Test that invalid price formats are rejected."""
    price_changes = [{"sku": "TEST-007", "new_price": "not-a-number"}]
    
    approved, rejected = enforce_policy(price_changes, {"TEST-007": 100.0})
    
    assert len(approved) == 0
    assert len(rejected) == 1
    assert rejected[0]["reject_reason"] == "invalid_price_format"

