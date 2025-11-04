# Generate Price Events Test Data

## Overview

You can generate realistic `price_events` test data in two ways:
1. **Via API endpoint** (curl) - Best for Railway/production
2. **Via Python script** - Best for local development

## Method 1: Via API (curl) ⭐ Recommended

### Generate 10 price events (default):
```bash
curl -X POST https://your-railway-app.railway.app/api/generate-price-events
```

### Generate specific number of events:
```bash
curl -X POST "https://your-railway-app.railway.app/api/generate-price-events?count=20"
```

### Example Response:
```json
{
  "status": "success",
  "message": "Generated 20 price events",
  "count": 20
}
```

### For Local Development:
```bash
curl -X POST http://localhost:8000/api/generate-price-events?count=15
```

## Method 2: Via Python Script

### Generate 10 events (default):
```bash
cd suppliersync
python generate_price_events.py
```

### Generate specific number:
```bash
python generate_price_events.py --count 25
```

## What It Does

The script generates realistic price events:

1. **Randomly selects** active products from your catalog
2. **Generates price changes** between -15% and +10% (more likely to decrease)
3. **Creates realistic timestamps** spread over the last 7 days
4. **Uses realistic reasons**:
   - `competitive_adjustment`
   - `seasonal_pricing`
   - `inventory_clearance`
   - `margin_optimization`
   - `market_demand_increase`
   - `promotional_pricing`
   - `cost_adjustment`
   - `price_match_competitor`
   - `volume_discount`
   - `introductory_pricing`

5. **Updates product prices** - Also updates the `products.retail_price` to match the new price
6. **Creates run_id** - Each event gets a unique UUID for traceability

## Requirements

- Database must have **active products** (run `populate_inventory.py` first if needed)
- Products must exist in `products` table with `is_active=1`

## Example Usage Workflow

### Step 1: Ensure products exist
```bash
# Via API
curl -X POST https://your-railway-app.railway.app/api/populate

# Or locally
cd suppliersync
python populate_inventory.py
```

### Step 2: Generate price events
```bash
# Via API
curl -X POST "https://your-railway-app.railway.app/api/generate-price-events?count=20"

# Or locally
cd suppliersync
python generate_price_events.py --count 20
```

### Step 3: Verify in dashboard
Visit your dashboard and check:
- **Stats Cards** - Should show price events count
- **Recent Price Events** table - Should show new events
- **Catalog** - Prices should be updated

## Rate Limits

- **API endpoint**: 10 requests per minute
- **Max events per request**: 50 (prevents abuse)

## Example Output

When you run the script, you'll see:
```
Generating 20 price events...
Found 20 active products
  ✓ Created event 1/20: SOF-001 $899.00 → $849.00 (competitive_adjustment)
  ✓ Created event 2/20: TBL-002 $649.00 → $599.00 (seasonal_pricing)
  ✓ Created event 3/20: CHA-003 $249.00 → $229.00 (margin_optimization)
  ...

✅ Generated 20 price events successfully!
```

## Verify Events Were Created

### Check via API:
```bash
curl https://your-railway-app.railway.app/api/price-events?limit=10
```

### Check stats:
```bash
curl https://your-railway-app.railway.app/api/stats
```

Should show `approved_price_events` count increased!

## Notes

- **Price events update product prices** - The script updates `products.retail_price` to match the new price
- **Timestamps are realistic** - Events are spread over the last 7 days
- **No duplicates** - Each event is unique with its own `run_id`
- **Safe to run multiple times** - Will generate new events each time

## Troubleshooting

### "No active products found"
- Run `populate_inventory.py` first to create products
- Or use `/api/populate` endpoint

### "Failed to generate price events"
- Check Railway logs for details
- Ensure database is accessible
- Verify products table exists

### Events not showing in dashboard
- Wait a few seconds for database to commit
- Refresh the dashboard
- Check that `ORCHESTRATOR_API_URL` is set correctly in Vercel

