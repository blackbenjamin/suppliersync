
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
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS eval_metrics (
  id INTEGER PRIMARY KEY,
  run_id TEXT, metric TEXT, value REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
