"""
Database migration script to add rejected_prices table and update schema.
Run with: python migrate_db.py
"""

import os
import sqlite3

DB_PATH = os.getenv("SQLITE_PATH", "suppliersync.db")

def migrate():
    """Add rejected_prices table and ensure all schema updates are applied."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print(f"Migrating database: {DB_PATH}")
    
    # Create rejected_prices table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rejected_prices (
            id INTEGER PRIMARY KEY, sku TEXT, proposed_price REAL, current_price REAL,
            reject_reason TEXT, reject_details TEXT, run_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created rejected_prices table")
    
    # Add run_id columns if missing (idempotent)
    # Security: Validate table names to prevent SQL injection
    from core.security import validate_table_name
    allowed_tables = ("price_events", "supplier_updates", "cx_events", "agent_logs")
    for table in allowed_tables:
        # Validate table name is in whitelist (defense in depth)
        if not validate_table_name(table, allowed_tables):
            print(f"⚠️  Skipping invalid table name: {table}")
            continue
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN run_id TEXT")
            print(f"✅ Added run_id column to {table}")
        except sqlite3.OperationalError:
            print(f"  ✓ run_id column already exists in {table}")
    
    # Create indexes if they don't exist
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rejected_prices_sku_created ON rejected_prices(sku, created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_price_events_sku_created ON price_events(sku, created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cx_events_sku_created ON cx_events(sku, created_at)")
    print("✅ Created/verified indexes")
    
    conn.commit()
    conn.close()
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    migrate()

