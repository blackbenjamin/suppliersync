"""
Generate realistic price_events test data for SupplierSync.
Run with: python generate_price_events.py [--count N]
Or use via API: POST /api/generate-price-events?count=N
"""

import os
import sqlite3
import uuid
from datetime import datetime, timedelta
import random
import argparse

DB_PATH = os.getenv("SQLITE_PATH", "suppliersync.db")

# Realistic price change reasons
PRICE_REASONS = [
    "competitive_adjustment",
    "seasonal_pricing",
    "inventory_clearance",
    "margin_optimization",
    "market_demand_increase",
    "promotional_pricing",
    "cost_adjustment",
    "price_match_competitor",
    "volume_discount",
    "introductory_pricing",
]

def generate_price_events(count: int = 10):
    """
    Generate realistic price_events data for testing.
    
    Args:
        count: Number of price events to generate
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print(f"Generating {count} price events...")
    
    # Get active products
    products = conn.execute(
        "SELECT sku, retail_price FROM products WHERE is_active=1"
    ).fetchall()
    
    if not products:
        print("❌ No active products found. Run populate_inventory.py first!")
        conn.close()
        return 0
    
    print(f"Found {len(products)} active products")
    
    events_created = 0
    base_time = datetime.now()
    
    for i in range(count):
        # Pick a random product
        product = random.choice(products)
        sku = product["sku"]
        current_price = float(product["retail_price"])
        
        # Generate realistic price change (-15% to +10% range)
        # More likely to decrease than increase (realistic for retail)
        change_pct = random.uniform(-0.15, 0.10)
        if random.random() < 0.7:  # 70% chance of decrease
            change_pct = random.uniform(-0.15, -0.02)
        
        new_price = round(current_price * (1 + change_pct), 2)
        
        # Ensure minimum $0.01
        if new_price < 0.01:
            new_price = 0.01
        
        # Generate timestamp (spread over last 7 days)
        days_ago = random.uniform(0, 7)
        event_time = base_time - timedelta(days=days_ago)
        
        # Pick a random reason
        reason = random.choice(PRICE_REASONS)
        
        # Generate run_id
        run_id = str(uuid.uuid4())
        
        # Insert price event
        conn.execute(
            """INSERT INTO price_events(sku, prev_price, new_price, reason, run_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (sku, current_price, new_price, reason, run_id, event_time.isoformat())
        )
        
        # Update product's retail_price to match the new price
        conn.execute(
            "UPDATE products SET retail_price = ? WHERE sku = ?",
            (new_price, sku)
        )
        
        events_created += 1
        print(f"  ✓ Created event {i+1}/{count}: {sku} ${current_price:.2f} → ${new_price:.2f} ({reason})")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Generated {events_created} price events successfully!")
    return events_created


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate price events test data")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of price events to generate (default: 10)"
    )
    args = parser.parse_args()
    
    generate_price_events(args.count)

