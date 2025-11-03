#!/bin/bash
# Integration test script for SupplierSync
# Tests FastAPI server, database, and dashboard connectivity

set -e

echo "🧪 SupplierSync Integration Test"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: FastAPI health endpoint
echo "1️⃣  Testing FastAPI health endpoint..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health)
    echo -e "${GREEN}✓${NC} FastAPI is running"
    echo "   Response: $HEALTH"
else
    echo -e "${RED}✗${NC} FastAPI is not running on port 8000"
    echo "   Start it with: cd suppliersync && source .venv/bin/activate && uvicorn api:app --reload --port 8000"
    exit 1
fi
echo ""

# Check 2: Database file exists
echo "2️⃣  Checking database file..."
DB_PATH="/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/suppliersync/suppliersync.db"
if [ -f "$DB_PATH" ]; then
    SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "${GREEN}✓${NC} Database exists: $DB_PATH ($SIZE)"
else
    echo -e "${YELLOW}⚠${NC} Database file not found: $DB_PATH"
    echo "   Run: cd suppliersync && python main.py (will initialize DB)"
fi
echo ""

# Check 3: Test database connectivity from Python
echo "3️⃣  Testing database connectivity (Python)..."
cd /Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/suppliersync
source .venv/bin/activate 2>/dev/null || true
if python -c "
import sqlite3
import os
db_path = os.getenv('SQLITE_PATH', 'suppliersync.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products WHERE is_active=1')
count = cursor.fetchone()[0]
print(f'Active products: {count}')
conn.close()
" 2>/dev/null; then
    PRODUCTS=$(python -c "
import sqlite3
import os
db_path = os.getenv('SQLITE_PATH', 'suppliersync.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products WHERE is_active=1')
count = cursor.fetchone()[0]
print(count)
conn.close()
" 2>/dev/null)
    echo -e "${GREEN}✓${NC} Database accessible from Python ($PRODUCTS active products)"
else
    echo -e "${RED}✗${NC} Cannot connect to database from Python"
fi
echo ""

# Check 4: Test orchestrate endpoint (health check - may fail if no API key)
echo "4️⃣  Testing orchestrate endpoint..."
if curl -s -X POST http://localhost:8000/orchestrate -H "Content-Type: application/json" > /tmp/orch_response.json 2>&1; then
    RESPONSE=$(cat /tmp/orch_response.json)
    if echo "$RESPONSE" | grep -q "run_id"; then
        echo -e "${GREEN}✓${NC} Orchestrate endpoint working (full orchestration ran)"
        echo "   Response preview: $(echo $RESPONSE | head -c 100)..."
    elif echo "$RESPONSE" | grep -q "OPENAI_API_KEY"; then
        echo -e "${YELLOW}⚠${NC} Orchestrate endpoint accessible but OPENAI_API_KEY not set"
        echo "   This is OK - endpoint structure is working"
        echo "   Set OPENAI_API_KEY in .env to test full orchestration"
    else
        echo -e "${YELLOW}⚠${NC} Orchestrate endpoint returned unexpected response"
        echo "   Response: $RESPONSE"
    fi
else
    echo -e "${RED}✗${NC} Cannot reach orchestrate endpoint"
fi
echo ""

# Check 5: Dashboard dev server
echo "5️⃣  Testing dashboard server..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Dashboard is running on port 3000"
    echo "   Open: http://localhost:3000"
else
    echo -e "${YELLOW}⚠${NC} Dashboard is not running on port 3000"
    echo "   Start it with: cd dashboard && npm run dev"
fi
echo ""

# Check 6: Environment variables
echo "6️⃣  Checking environment configuration..."
if [ -f "/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/suppliersync/.env" ]; then
    if grep -q "OPENAI_API_KEY" "/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/suppliersync/.env" && ! grep -q "OPENAI_API_KEY=$" "/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/suppliersync/.env"; then
        echo -e "${GREEN}✓${NC} Python .env file exists and has OPENAI_API_KEY set"
    else
        echo -e "${YELLOW}⚠${NC} Python .env file exists but OPENAI_API_KEY not set"
    fi
else
    echo -e "${YELLOW}⚠${NC} Python .env file not found"
fi

if [ -f "/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/dashboard/.env.local" ]; then
    if grep -q "SQLITE_PATH=" "/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/dashboard/.env.local" && ! grep -q "SQLITE_PATH=/absolute/path" "/Users/benjaminblack/projects/ai-demos/experiments/suppliersync_demo/dashboard/.env.local"; then
        echo -e "${GREEN}✓${NC} Dashboard .env.local exists and has SQLITE_PATH set"
    else
        echo -e "${YELLOW}⚠${NC} Dashboard .env.local exists but SQLITE_PATH not configured correctly"
    fi
else
    echo -e "${YELLOW}⚠${NC} Dashboard .env.local not found"
fi
echo ""

echo "================================"
echo "📊 Test Summary"
echo "================================"
echo ""
echo "✅ Next steps:"
echo "   1. Ensure FastAPI server is running: cd suppliersync && uvicorn api:app --reload --port 8000"
echo "   2. Ensure Dashboard is running: cd dashboard && npm run dev"
echo "   3. Set OPENAI_API_KEY in suppliersync/.env to test full orchestration"
echo "   4. Open http://localhost:3000 and click 'Run Orchestration' button"
echo ""

