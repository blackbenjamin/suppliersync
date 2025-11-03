
import os, sqlite3, pandas as pd
from agents.orchestrator import Orchestrator

DB_PATH = os.getenv("SQLITE_PATH", "suppliersync.db")

with open("db/schema.sql", "r") as f:
    SCHEMA = f.read()

SEED_PRODUCTS = "data/seed_products.csv"
SEED_SUPPLIERS = "data/seed_suppliers.csv"

def init_db():
    need_seed = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.executescript(SCHEMA)
    if need_seed:
        # Seed suppliers
        df_sup = pd.read_csv(SEED_SUPPLIERS)
        for _, r in df_sup.iterrows():
            conn.execute("INSERT INTO suppliers(id, name, sla_days) VALUES (?,?,?)",
                         (int(r.id), r.name, int(r.sla_days)))
        # Seed products
        df = pd.read_csv(SEED_PRODUCTS)
        for _, r in df.iterrows():
            conn.execute("INSERT INTO products(sku, name, category, wholesale_price, retail_price, supplier_id) VALUES (?,?,?,?,?,?)",
                         (r.sku, r.name, r.category, float(r.wholesale_price), float(r.retail_price), int(r.supplier_id)))
        conn.commit()
    conn.close()

def run_once():
    orch = Orchestrator(DB_PATH)
    result = orch.step()
    print("=== Orchestration Result ===")
    for k, v in result.items():
        print(k, "->", v)

if __name__ == "__main__":
    init_db()
    run_once()
