
import json
from typing import List
from core.llm import chat_json
from core.prompts import SUPPLIER_PROMPT
from core.types import SupplierUpdate, AgentTelemetry, AgentResult

def propose_supplier_updates(context: str) -> AgentResult:
    system = "You propose supplier updates as JSON."
    user = f"{SUPPLIER_PROMPT}\nCONTEXT:\n{context}"
    resp, latency, tokens = chat_json(system, user)
    tokens_in, tokens_out = tokens
    items: List[dict] = []
    try:
        raw = json.loads(resp)
        raw_items = raw.get("updates", raw)
        for r in raw_items or []:
            try:
                su = SupplierUpdate(**r)
                items.append(su.model_dump())
            except Exception:
                continue
    except Exception:
        items = []
    telemetry = AgentTelemetry(
        agent="supplier",
        step="propose_updates",
        prompt=user,
        response=resp or "",
        tokens_in=int(tokens_in or 0),
        tokens_out=int(tokens_out or 0),
        latency_ms=int(latency or 0),
        cost_usd=0.0,
    )
    return AgentResult(items=items, telemetry=telemetry)
