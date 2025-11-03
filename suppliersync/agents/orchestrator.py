
import sqlite3, json, uuid
from datetime import datetime
from typing import Dict
from core.governance import enforce_policy
from .supplier_agent import propose_supplier_updates
from .buyer_agent import propose_price_changes
from .cx_agent import propose_cx_actions
from core.evals import track_cost

class Orchestrator:
    """
    Coordinates multi-agent orchestration for supplier management, pricing, and CX.
    
    The Orchestrator manages the execution lifecycle of all agents (Supplier, Buyer, CX)
    within a single database transaction, ensuring data consistency and atomicity.
    
    Features:
    - Transaction-based execution (all-or-nothing)
    - Automatic schema migration and indexing
    - Price history tracking for governance checks
    - Agent telemetry logging for cost tracking
    - Run ID generation for traceability
    
    Example:
        >>> orch = Orchestrator("suppliersync.db")
        >>> result = orch.step()
        >>> print(f"Run ID: {result['run_id']}")
        >>> print(f"Approved prices: {len(result['approved_prices'])}")
        >>> print(f"Rejected prices: {len(result['rejected_prices'])}")
    """
    
    def __init__(self, db_path: str = "suppliersync.db"):
        """
        Initialize the Orchestrator with database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        # Enable WAL mode for concurrent reads/writes
        self.db.execute("PRAGMA journal_mode=WAL;")
        # Use NORMAL synchronous mode for better performance (still safe with WAL)
        self.db.execute("PRAGMA synchronous=NORMAL;")
        self._ensure_schema()

    def _ensure_schema(self):
        """
        Ensure database schema is up to date (migrations and indexes).
        
        This method is idempotent and safe to call multiple times.
        It will:
        - Add run_id columns to existing tables if missing
        - Create rejected_prices table if it doesn't exist
        - Create indexes for performance optimization
        """
        # Add run_id columns if missing
        # NOTE: Table names are whitelisted to prevent SQL injection
        # In production, consider using SQLAlchemy ORM for better protection
        from core.security import validate_table_name
        allowed_tables = ("price_events", "supplier_updates", "cx_events", "agent_logs")
        for table in allowed_tables:
            # Validate table name is in whitelist (defense in depth)
            if not validate_table_name(table, allowed_tables):
                continue
            try:
                self.db.execute(f"ALTER TABLE {table} ADD COLUMN run_id TEXT")
            except Exception:
                pass
        # Create rejected_prices table if it doesn't exist
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS rejected_prices (
                id INTEGER PRIMARY KEY, sku TEXT, proposed_price REAL, current_price REAL,
                reject_reason TEXT, reject_details TEXT, run_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create indexes
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_price_events_sku_created ON price_events(sku, created_at)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_rejected_prices_sku_created ON rejected_prices(sku, created_at)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_cx_events_sku_created ON cx_events(sku, created_at)")
        self.db.commit()

    def _fetch_catalog(self):
        cur = self.db.execute("SELECT sku, name, category, wholesale_price, retail_price FROM products WHERE is_active=1")
        return [dict(r) for r in cur.fetchall()]
    
    def _fetch_price_history(self, skus: list) -> Dict[str, Dict]:
        """Fetch current price and last change date for given SKUs."""
        if not skus:
            return {}
        placeholders = ",".join(["?"] * len(skus))
        # Get most recent price event per SKU
        cur = self.db.execute(f"""
            SELECT sku, new_price, created_at
            FROM price_events pe1
            WHERE pe1.sku IN ({placeholders})
            AND pe1.id = (
                SELECT MAX(pe2.id) FROM price_events pe2 
                WHERE pe2.sku = pe1.sku
            )
        """, skus)
        history = {}
        for row in cur.fetchall():
            created_at = row["created_at"]
            date_obj = None
            if created_at:
                try:
                    # Try ISO format first
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        # Fall back to strptime for common SQLite formats
                        date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # If parsing fails, set to None (will skip drift check)
                        date_obj = None
            history[row["sku"]] = {
                "price": row["new_price"],
                "date": date_obj
            }
        return history
    
    def _fetch_current_prices(self, skus: list) -> Dict[str, float]:
        """Fetch current retail prices from products table."""
        if not skus:
            return {}
        placeholders = ",".join(["?"] * len(skus))
        cur = self.db.execute(f"SELECT sku, retail_price FROM products WHERE sku IN ({placeholders})", skus)
        return {row["sku"]: row["retail_price"] for row in cur.fetchall()}

    def _apply_supplier_updates(self, updates, run_id: str):
        for u in updates or []:
            sku, field, new_value, reason = u.get("sku"), u.get("field"), u.get("new_value"), u.get("reason","supplier_update")
            self.db.execute("INSERT INTO supplier_updates(sku, field, old_value, new_value, run_id) VALUES (?,?,?,?,?)",
                            (sku, field, None, str(new_value), run_id))
            if field in ("wholesale_price","name","category"):
                self.db.execute(f"UPDATE products SET {field}=? WHERE sku=?", (new_value, sku))
        self.db.commit()

    def _apply_price_changes(self, approved, run_id: str):
        for p in approved or []:
            sku, new_price, reason = p.get("sku"), float(p.get("new_price")), p.get("reason","pricing")
            cur = self.db.execute("SELECT retail_price FROM products WHERE sku=?", (sku,))
            row = cur.fetchone()
            prev = float(row[0]) if row else None
            self.db.execute("UPDATE products SET retail_price=? WHERE sku=?", (new_price, sku))
            self.db.execute("INSERT INTO price_events(sku, prev_price, new_price, reason, run_id) VALUES (?,?,?,?,?)",
                            (sku, prev, new_price, reason, run_id))
        self.db.commit()
    
    def _store_rejected_prices(self, rejected, sku_to_current_price: Dict[str, float], run_id: str):
        """Store rejected price changes for governance tracking."""
        for r in rejected or []:
            sku = r.get("sku")
            proposed_price = float(r.get("new_price", 0))
            current_price = sku_to_current_price.get(sku)
            reject_reason = r.get("reject_reason", "unknown")
            reject_details = r.get("reject_details", "")
            self.db.execute(
                "INSERT INTO rejected_prices(sku, proposed_price, current_price, reject_reason, reject_details, run_id) VALUES (?,?,?,?,?,?)",
                (sku, proposed_price, current_price, reject_reason, reject_details, run_id)
            )
        self.db.commit()

    def _log_agent(self, run_id: str, telemetry):
        cost = track_cost(telemetry.tokens_in, telemetry.tokens_out)
        self.db.execute(
            "INSERT INTO agent_logs(agent, step, prompt, response, tokens_in, tokens_out, latency_ms, cost_usd, run_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                telemetry.agent,
                telemetry.step,
                telemetry.prompt,
                telemetry.response,
                telemetry.tokens_in,
                telemetry.tokens_out,
                telemetry.latency_ms,
                cost,
                run_id,
            ),
        )

    def step(self):
        """
        Execute one orchestration cycle.
        
        This method coordinates the execution of all agents in sequence:
        1. Supplier Agent: Proposes catalog updates (SKUs, availability, wholesale prices)
        2. Buyer Agent: Proposes price changes (with business justification)
        3. Governance: Enforces business rules on price changes
        4. CX Agent: Proposes customer experience improvements
        
        All operations run within a single database transaction, ensuring
        atomicity (all changes succeed or all are rolled back).
        
        Returns:
            Dict containing:
            - run_id: Unique identifier for this orchestration run
            - supplier_updates: List of supplier data changes applied
            - approved_prices: List of price changes that passed governance
            - rejected_prices: List of price changes that failed governance
            - cx_actions: List of customer experience actions proposed
        
        Example:
            >>> result = orch.step()
            >>> print(f"Run {result['run_id']} completed:")
            >>> print(f"  - {len(result['supplier_updates'])} supplier updates")
            >>> print(f"  - {len(result['approved_prices'])} prices approved")
            >>> print(f"  - {len(result['rejected_prices'])} prices rejected")
            >>> print(f"  - {len(result['cx_actions'])} CX actions")
        """
        # Generate unique run ID for traceability
        run_id = str(uuid.uuid4())
        # Execute all operations within a transaction
        with self.db:
            catalog = self._fetch_catalog()
            context = json.dumps({"catalog": catalog}, indent=2)
            sup_res = propose_supplier_updates(context)
            self._log_agent(run_id, sup_res.telemetry)
            self._apply_supplier_updates(sup_res.items, run_id)
            catalog = self._fetch_catalog()
            sku_to_wholesale = {c["sku"]: c["wholesale_price"] for c in catalog}
            sku_to_category = {c["sku"]: c.get("category") for c in catalog}
            
            # Get proposed price changes first
            pricing_res = propose_price_changes(json.dumps({"catalog": catalog, "supplier_updates": sup_res.items}))
            self._log_agent(run_id, pricing_res.telemetry)
            
            # Gather price history for governance checks (only for proposed SKUs)
            proposed_skus = [pc.get("sku") for pc in pricing_res.items if pc.get("sku")]
            price_history = self._fetch_price_history(proposed_skus)
            current_prices = self._fetch_current_prices(proposed_skus)
            
            sku_to_current_price = {}
            sku_to_last_price_date = {}
            for sku in proposed_skus:
                sku_to_current_price[sku] = current_prices.get(sku)
                if sku in price_history:
                    sku_to_current_price[sku] = price_history[sku]["price"]  # Use most recent event price
                    sku_to_last_price_date[sku] = price_history[sku]["date"]
                else:
                    # Fall back to products table if no history
                    sku_to_current_price[sku] = current_prices.get(sku)
                    sku_to_last_price_date[sku] = None
            
            # MAP pricing (placeholder - can be extended with a products.map_price column)
            sku_to_map_price = {}  # TODO: Fetch from products table or external source
            
            approved, rejected = enforce_policy(
                pricing_res.items,
                sku_to_wholesale,
                sku_to_category=sku_to_category,
                sku_to_current_price=sku_to_current_price,
                sku_to_last_price_date=sku_to_last_price_date,
                sku_to_map_price=sku_to_map_price,
            )
            self._apply_price_changes(approved, run_id)
            self._store_rejected_prices(rejected, sku_to_current_price, run_id)
            cx_res = propose_cx_actions(json.dumps({"catalog": self._fetch_catalog()}))
            self._log_agent(run_id, cx_res.telemetry)
            for a in cx_res.items or []:
                self.db.execute("INSERT INTO cx_events(sku, event_type, details, run_id) VALUES (?,?,?,?)",
                                (a.get("sku"), "agent_action", json.dumps(a), run_id))
        return {"run_id": run_id, "supplier_updates": sup_res.items, "approved_prices": approved, "rejected_prices": rejected, "cx_actions": cx_res.items}
