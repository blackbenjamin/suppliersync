"""
Database migration script to initialize schema and add rejected_prices table.
Run with: python migrate_db.py
"""

import os
import sqlite3

DB_PATH = os.getenv("SQLITE_PATH", "suppliersync.db")

# Load schema from schema.sql
SCHEMA_SQL = """
-- Core reference
CREATE TABLE IF NOT EXISTS suppliers (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, sla_days INTEGER DEFAULT 3
);
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY, sku TEXT UNIQUE, name TEXT, category TEXT,
  wholesale_price REAL, retail_price REAL, supplier_id INTEGER,
  is_active INTEGER DEFAULT 1,
  FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Events (ingest & orchestration)
CREATE TABLE IF NOT EXISTS price_events (
  id INTEGER PRIMARY KEY, sku TEXT, prev_price REAL, new_price REAL,
  reason TEXT, run_id TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS rejected_prices (
  id INTEGER PRIMARY KEY, sku TEXT, proposed_price REAL, current_price REAL,
  reject_reason TEXT, reject_details TEXT, run_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS supplier_updates (
  id INTEGER PRIMARY KEY, sku TEXT, field TEXT, old_value TEXT, new_value TEXT, run_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cx_events (
  id INTEGER PRIMARY KEY, sku TEXT, event_type TEXT, details TEXT, run_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Observability
CREATE TABLE IF NOT EXISTS agent_logs (
  id INTEGER PRIMARY KEY,
  agent TEXT, step TEXT, prompt TEXT, response TEXT,
  tokens_in INTEGER, tokens_out INTEGER,
  latency_ms INTEGER, cost_usd REAL,
  run_id TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS eval_metrics (
  id INTEGER PRIMARY KEY,
  run_id TEXT, metric TEXT, value REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def migrate():
    """Initialize database schema and ensure all schema updates are applied."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print(f"Migrating database: {DB_PATH}")
    
    # Create all tables from schema first
    conn.executescript(SCHEMA_SQL)
    print("✅ Created all tables from schema")
    
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

