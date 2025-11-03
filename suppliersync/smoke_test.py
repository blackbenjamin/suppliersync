import os
import sqlite3
from typing import Tuple

from main import init_db, run_once, DB_PATH


def count_rows(conn: sqlite3.Connection) -> Tuple[int, int, int, int]:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products WHERE is_active=1")
    products = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM price_events")
    price_events = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM supplier_updates")
    supplier_updates = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cx_events")
    cx_events = cur.fetchone()[0]
    return products, price_events, supplier_updates, cx_events


def main():
    # Ensure DB path from env is honored
    db_path = os.getenv("SQLITE_PATH", DB_PATH)
    print(f"Using DB at: {db_path}")

    # Initialize schema and seed if first run
    init_db()

    # Before counts
    conn = sqlite3.connect(db_path)
    before = count_rows(conn)
    print(f"Before -> products={before[0]} price_events={before[1]} supplier_updates={before[2]} cx_events={before[3]}")

    # Run one orchestration
    run_once()

    # After counts
    after = count_rows(conn)
    print(f"After  -> products={after[0]} price_events={after[1]} supplier_updates={after[2]} cx_events={after[3]}")

    # Simple assertion: events should be non-decreasing
    assert after[1] >= before[1], "price_events did not increase or stay same"
    assert after[2] >= before[2], "supplier_updates did not increase or stay same"
    assert after[3] >= before[3], "cx_events did not increase or stay same"
    print("Smoke test passed.")


if __name__ == "__main__":
    main()


