
export type Product = {
  id: number;
  sku: string;
  name: string;
  category: string;
  wholesale_price: number;
  retail_price: number;
  supplier_id: number;
  is_active: 0 | 1;
};

export type PriceEvent = {
  id: number; sku: string; prev_price: number; new_price: number; reason: string; created_at: string;
};

export type CXEvent = {
  id: number; sku: string; event_type: string; details: string; created_at: string;
};
