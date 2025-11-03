
from pydantic import BaseModel, Field
from typing import Optional, Literal, Union, List

class Supplier(BaseModel):
    id: int
    name: str
    sla_days: int = 3

class Product(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    wholesale_price: float
    retail_price: float
    supplier_id: int
    is_active: bool = True

class CXEvent(BaseModel):
    sku: str
    event_type: str  # "return", "incident", "question"
    details: str


class SupplierUpdate(BaseModel):
    sku: str
    field: Literal["wholesale_price", "name", "category"]
    new_value: Union[float, str]
    reason: Optional[str] = None


class PriceChange(BaseModel):
    sku: str
    new_price: float = Field(gt=0)
    reason: Optional[str] = None


class CXAction(BaseModel):
    sku: str
    action: str
    details: str


class AgentTelemetry(BaseModel):
    agent: str
    step: str
    prompt: str
    response: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float


class AgentResult(BaseModel):
    items: List[dict]
    telemetry: AgentTelemetry
