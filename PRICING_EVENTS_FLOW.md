# What Triggers Pricing Events in SupplierSync

## Overview

Pricing events are created when the **Buyer Agent** proposes price changes that pass **Governance Policy** checks. Here's the complete flow:

## Inputs & Flow

### 1. **Trigger: Manual Orchestration Run**

The system is triggered when a user clicks **"Run Orchestration"** in the dashboard, which calls:
- **API Endpoint**: `POST /orchestrate`
- **Handler**: `Orchestrator.step()` method

### 2. **Agent Execution Sequence**

Each orchestration run executes agents in this order:

#### **Step 1: Supplier Agent** (`propose_supplier_updates`)
- **Input**: Current product catalog (all active SKUs with prices, categories, suppliers)
- **Process**: LLM analyzes catalog and proposes supplier updates:
  - New wholesale prices
  - Product availability changes
  - SKU updates (name, category changes)
- **Output**: List of supplier updates applied to database
- **Prompt**: `SUPPLIER_PROMPT` - "You are the Supplier Agent. You announce product availability and wholesale price changes..."

#### **Step 2: Buyer Agent** (`propose_price_changes`) ⭐ **PRICING EVENTS START HERE**
- **Input**: 
  - Updated catalog (after supplier updates)
  - Supplier updates from Step 1
- **Process**: LLM analyzes and proposes retail price changes:
  - Considers margin optimization
  - Price competitiveness
  - SKU coverage
  - Return risk
  - Competitor price hints (simulated)
- **Output**: List of proposed price changes (`PriceChange` objects)
- **Prompt**: `BUYER_PROMPT` - "You are the Buyer/Pricing Agent. Optimize retail prices to balance margin..."

#### **Step 3: Governance Policy** (`enforce_policy`)
- **Input**: 
  - Proposed price changes from Buyer Agent
  - Current wholesale prices
  - Current retail prices
  - Price history (last price change date)
  - Product categories
  - MAP prices (if configured)
- **Rules Enforced**:
  1. ✅ **Wholesale Check**: Retail price must be >= wholesale price
  2. ✅ **Margin Check**: Margin must be >= 5% (configurable via `MIN_MARGIN_PCT`)
  3. ✅ **Daily Drift Check**: Price change must be <= 20% per day (configurable via `MAX_DAILY_PRICE_DRIFT`)
  4. ✅ **Category Filter**: Must pass allow/block list (configurable via `BLOCKED_CATEGORIES`, `ALLOWED_CATEGORIES`)
  5. ✅ **MAP Enforcement**: Must respect MAP if set (placeholder)
- **Output**: Two lists:
  - **Approved prices**: Pass all rules → Create `price_events`
  - **Rejected prices**: Fail rules → Create `rejected_prices` records

#### **Step 4: Apply Approved Prices** (`_apply_price_changes`)
- **Process**: For each approved price change:
  1. Updates `products.retail_price` in database
  2. **Creates `price_events` record** with:
     - `sku`: Product SKU
     - `prev_price`: Previous retail price
     - `new_price`: New retail price
     - `reason`: Reason from Buyer Agent
     - `run_id`: Unique orchestration run ID
     - `created_at`: Timestamp

#### **Step 5: CX Agent** (`propose_cx_actions`)
- **Input**: Updated catalog
- **Process**: Analyzes customer experience and proposes actions
- **Output**: CX events (not directly related to pricing)

## Key Data Sources

### **Database Tables Used**:
1. **`products`** - Current catalog (SKUs, prices, categories, suppliers)
2. **`price_events`** - Historical price changes (for drift checks)
3. **`suppliers`** - Supplier information

### **LLM Context Provided**:
```json
{
  "catalog": [
    {
      "sku": "SOF-001",
      "name": "Westwood 84\" Gray Fabric Sofa...",
      "category": "Couches",
      "wholesale_price": 520.00,
      "retail_price": 899.00
    },
    ...
  ],
  "supplier_updates": [
    {
      "sku": "SOF-001",
      "field": "wholesale_price",
      "new_value": 510.00,
      "reason": "market_signal"
    }
  ]
}
```

## What Creates a Pricing Event Record?

A `price_events` record is created when:

1. ✅ Buyer Agent proposes a price change
2. ✅ Governance policy approves it (passes all rules)
3. ✅ Database is updated with new price
4. ✅ `price_events` table is inserted with:
   ```sql
   INSERT INTO price_events(sku, prev_price, new_price, reason, run_id) 
   VALUES (?, ?, ?, ?, ?)
   ```

## What Does NOT Create a Pricing Event?

- ❌ **Rejected prices** → Stored in `rejected_prices` table instead
- ❌ **Supplier updates** (wholesale price changes) → Stored in `supplier_updates` table
- ❌ **CX actions** → Stored in `cx_events` table

## Configuration

### **Environment Variables** (affect pricing event creation):
- `MIN_MARGIN_PCT` - Minimum margin required (default: 0.05 = 5%)
- `MAX_DAILY_PRICE_DRIFT` - Max daily price change (default: 0.20 = 20%)
- `BLOCKED_CATEGORIES` - Categories to block (comma-separated)
- `ALLOWED_CATEGORIES` - Categories to allow (whitelist, comma-separated)

### **Governance Rules** (affect approval/rejection):
1. **Margin Rule**: `(retail_price - wholesale_price) / retail_price >= MIN_MARGIN_PCT`
2. **Drift Rule**: `abs(new_price - current_price) / current_price <= MAX_DAILY_PRICE_DRIFT`
3. **Category Rule**: Category must not be in `BLOCKED_CATEGORIES`, and if `ALLOWED_CATEGORIES` is set, must be in that list

## Example Flow

```
1. User clicks "Run Orchestration"
   ↓
2. Supplier Agent analyzes catalog
   → Proposes: "Reduce SOF-001 wholesale from $520 to $510"
   → Applied to database
   ↓
3. Buyer Agent analyzes updated catalog
   → Proposes: "Reduce SOF-001 retail from $899 to $879"
   ↓
4. Governance checks:
   → Margin: ($879 - $510) / $879 = 42% ✅ (passes 5% minimum)
   → Drift: |$879 - $899| / $899 = 2.2% ✅ (passes 20% maximum)
   → Category: "Couches" ✅ (not blocked)
   → APPROVED ✅
   ↓
5. Database updated:
   → products.retail_price = $879
   → price_events INSERT: (sku='SOF-001', prev_price=899, new_price=879, reason='competitive_adjustment', run_id='...')
   ↓
6. Dashboard shows new price event ✅
```

## Summary

**Pricing events are created by**:
1. **Manual trigger**: User clicks "Run Orchestration" button
2. **Buyer Agent**: LLM proposes price changes based on catalog
3. **Governance**: Rules approve/reject proposals
4. **Database**: Approved prices create `price_events` records

**Key inputs**:
- Current product catalog (SKUs, prices, categories)
- Supplier updates from Supplier Agent
- Price history (for drift checks)
- Governance configuration (margin, drift, category rules)

**No external APIs** - Everything is simulated/LLM-generated based on the catalog data!

