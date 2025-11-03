
import json
from typing import List
from core.llm import chat_json
from core.prompts import BUYER_PROMPT
from core.types import PriceChange, AgentTelemetry, AgentResult

def propose_price_changes(context: str) -> AgentResult:
    system = "You output JSON list of price changes."
    user = f"{BUYER_PROMPT}\nCONTEXT:\n{context}"
    resp, latency, tokens = chat_json(system, user)
    tokens_in, tokens_out = tokens
    items: List[dict] = []
    try:
        raw = json.loads(resp)
        raw_items = raw.get("prices", raw)
        for r in raw_items or []:
            try:
                pc = PriceChange(**r)
                items.append(pc.model_dump())
            except Exception:
                continue
    except Exception:
        items = []
    telemetry = AgentTelemetry(
        agent="buyer",
        step="propose_price_changes",
        prompt=user,
        response=resp or "",
        tokens_in=int(tokens_in or 0),
        tokens_out=int(tokens_out or 0),
        latency_ms=int(latency or 0),
        cost_usd=0.0,
    )
    return AgentResult(items=items, telemetry=telemetry)
