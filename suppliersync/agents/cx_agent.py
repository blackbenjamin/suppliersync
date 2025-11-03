
import json
from typing import List
from core.llm import chat_json
from core.prompts import CX_PROMPT
from core.types import CXAction, AgentTelemetry, AgentResult

def propose_cx_actions(context: str) -> AgentResult:
    system = "You output JSON list of CX actions."
    user = f"{CX_PROMPT}\nCONTEXT:\n{context}"
    resp, latency, tokens = chat_json(system, user)
    tokens_in, tokens_out = tokens
    items: List[dict] = []
    try:
        raw = json.loads(resp)
        raw_items = raw.get("actions", raw)
        for r in raw_items or []:
            try:
                a = CXAction(**r)
                items.append(a.model_dump())
            except Exception:
                continue
    except Exception:
        items = []
    telemetry = AgentTelemetry(
        agent="cx",
        step="propose_actions",
        prompt=user,
        response=resp or "",
        tokens_in=int(tokens_in or 0),
        tokens_out=int(tokens_out or 0),
        latency_ms=int(latency or 0),
        cost_usd=0.0,
    )
    return AgentResult(items=items, telemetry=telemetry)
