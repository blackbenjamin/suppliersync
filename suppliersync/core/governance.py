
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Governance configuration (can be overridden via env vars)
MAX_DAILY_PRICE_DRIFT = float(os.getenv("MAX_DAILY_PRICE_DRIFT", "0.20"))  # 20% max change per day
MIN_MARGIN_PCT = float(os.getenv("MIN_MARGIN_PCT", "0.05"))  # 5% minimum margin
BLOCKED_CATEGORIES = set(os.getenv("BLOCKED_CATEGORIES", "").split(",")) if os.getenv("BLOCKED_CATEGORIES") else set()
ALLOWED_CATEGORIES = set(os.getenv("ALLOWED_CATEGORIES", "").split(",")) if os.getenv("ALLOWED_CATEGORIES") else None


def enforce_policy(
    price_changes: List[Dict],
    sku_to_wholesale: Dict[str, float],
    sku_to_category: Optional[Dict[str, str]] = None,
    sku_to_current_price: Optional[Dict[str, float]] = None,
    sku_to_last_price_date: Optional[Dict[str, Optional[datetime]]] = None,
    sku_to_map_price: Optional[Dict[str, Optional[float]]] = None,
) -> tuple[List[Dict], List[Dict]]:
    """
    Enforce business rules on price changes.
    
    This function applies governance rules to proposed price changes, separating
    them into approved and rejected categories. All rules are configurable via
    environment variables, enabling A/B testing and rapid policy iteration.
    
    Rules enforced (in order):
    1. **Wholesale Price Check**: Retail price must be >= wholesale price
    2. **Margin Check**: Margin must be >= MIN_MARGIN_PCT (default 5%)
    3. **Daily Price Drift**: Daily price change must be <= MAX_DAILY_PRICE_DRIFT (default 20%)
    4. **Category Allow/Block Lists**: Categories must pass allow/block list checks
    5. **MAP Enforcement**: Price must respect MAP (Minimum Advertised Price) if set
    
    Args:
        price_changes: List of proposed price changes, each with:
            - 'sku': Product SKU
            - 'new_price': Proposed retail price
        sku_to_wholesale: Mapping of SKU to wholesale price (required)
        sku_to_category: Optional mapping of SKU to category (for category filtering)
        sku_to_current_price: Optional mapping of SKU to current retail price (for drift checks)
        sku_to_last_price_date: Optional mapping of SKU to datetime of last price change
        sku_to_map_price: Optional mapping of SKU to MAP price (for MAP enforcement)
    
    Returns:
        Tuple of (approved_changes, rejected_changes) where:
        - approved_changes: List of price changes that passed all rules
        - rejected_changes: List of price changes that failed, each with:
            - 'sku': Product SKU
            - 'new_price': Proposed price
            - 'reject_reason': Short reason code (e.g., "margin_too_low")
            - 'reject_details': Detailed explanation
    
    Example:
        >>> approved, rejected = enforce_policy(
        ...     [{"sku": "WF-001", "new_price": 150.0}],
        ...     {"WF-001": 100.0},  # wholesale price
        ...     sku_to_current_price={"WF-001": 140.0}
        ... )
        >>> print(f"Approved: {len(approved)}, Rejected: {len(rejected)}")
    
    Note:
        All rules are configurable via environment variables:
        - MIN_MARGIN_PCT: Minimum profit margin (default: 0.05 = 5%)
        - MAX_DAILY_PRICE_DRIFT: Maximum daily price change (default: 0.20 = 20%)
        - BLOCKED_CATEGORIES: Comma-separated list of blocked categories
        - ALLOWED_CATEGORIES: Comma-separated list of allowed categories (whitelist)
    """
    approved, rejected = [], []
    sku_to_category = sku_to_category or {}
    sku_to_current_price = sku_to_current_price or {}
    sku_to_last_price_date = sku_to_last_price_date or {}
    sku_to_map_price = sku_to_map_price or {}
    
    for pc in price_changes or []:
        sku = pc.get("sku")
        if not sku:
            pc["reject_reason"] = "missing_sku"
            rejected.append(pc)
            continue
            
        # Parse new price
        try:
            new_price = float(pc.get("new_price", 0))
            if new_price <= 0:
                pc["reject_reason"] = "price_must_be_positive"
                pc["reject_details"] = f"Price must be greater than 0, got {new_price}"
                rejected.append(pc)
                continue
        except (ValueError, TypeError):
            pc["reject_reason"] = "invalid_price_format"
            pc["reject_details"] = f"Could not parse price: {pc.get('new_price')}"
            rejected.append(pc)
            continue
        
        # Rule 1: Category allow/block list
        category = sku_to_category.get(sku)
        if category:
            if ALLOWED_CATEGORIES is not None and category not in ALLOWED_CATEGORIES:
                pc["reject_reason"] = "category_not_allowed"
                pc["reject_details"] = f"Category '{category}' is not in allowed list: {sorted(ALLOWED_CATEGORIES)}"
                rejected.append(pc)
                continue
            if category in BLOCKED_CATEGORIES:
                pc["reject_reason"] = "category_blocked"
                pc["reject_details"] = f"Category '{category}' is blocked"
                rejected.append(pc)
                continue
        
        # Rule 2: Retail must be >= wholesale
        wholesale = float(sku_to_wholesale.get(sku, 0))
        if new_price < wholesale:
            pc["reject_reason"] = "retail_below_wholesale"
            pc["reject_details"] = f"Retail price ${new_price:.2f} cannot be below wholesale ${wholesale:.2f}"
            rejected.append(pc)
            continue
        
        # Rule 3: Minimum margin check
        margin_pct = (new_price - wholesale) / max(wholesale, 1e-6)
        if margin_pct < MIN_MARGIN_PCT:
            pc["reject_reason"] = "margin_below_minimum"
            pc["reject_details"] = f"Margin {margin_pct*100:.1f}% is below minimum {MIN_MARGIN_PCT*100:.0f}%"
            rejected.append(pc)
            continue
        
        # Rule 4: MAP (Minimum Advertised Price) enforcement
        map_price = sku_to_map_price.get(sku)
        if map_price is not None and new_price < map_price:
            pc["reject_reason"] = "below_map_price"
            pc["reject_details"] = f"Price ${new_price:.2f} is below MAP ${map_price:.2f}"
            rejected.append(pc)
            continue
        
        # Rule 5: Daily price drift check (max 20% change per day)
        current_price = sku_to_current_price.get(sku)
        last_change_date = sku_to_last_price_date.get(sku)
        
        if current_price is not None and last_change_date is not None:
            # Check if last change was today
            today = datetime.now().date()
            last_date = last_change_date.date() if isinstance(last_change_date, datetime) else last_change_date
            
            if last_date == today:
                price_change_pct = abs(new_price - current_price) / max(current_price, 1e-6)
                if price_change_pct > MAX_DAILY_PRICE_DRIFT:
                    pc["reject_reason"] = "daily_drift_exceeded"
                    pc["reject_details"] = (
                        f"Price change {price_change_pct*100:.1f}% exceeds daily limit "
                        f"{MAX_DAILY_PRICE_DRIFT*100:.0f}% (${current_price:.2f} -> ${new_price:.2f})"
                    )
                    rejected.append(pc)
                    continue
        
        # All checks passed
        approved.append(pc)
    
    return approved, rejected
