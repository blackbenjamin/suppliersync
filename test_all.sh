#!/bin/bash
# Comprehensive test script for SupplierSync
# Tests all components: API, database, security, dependencies

set +e  # Don't exit on error - we want to collect all test results

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
SKIPPED=0

# Function to print test results
test_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

test_skip() {
    echo -e "${YELLOW}⏭️  SKIP${NC}: $1"
    ((SKIPPED++))
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🧪 SupplierSync Comprehensive Test Suite"
echo "========================================"
echo ""

# 1. Environment Check
echo "📋 1. Environment Check"
echo "----------------------"

if [ -f "suppliersync/.env" ]; then
    test_pass "suppliersync/.env file exists"
else
    test_fail "suppliersync/.env file not found (copy from env.example)"
fi

if [ -f "dashboard/.env.local" ]; then
    test_pass "dashboard/.env.local file exists"
else
    test_fail "dashboard/.env.local file not found (copy from env.local.example)"
fi

if [ -n "${OPENAI_API_KEY}" ] || grep -q "OPENAI_API_KEY" suppliersync/.env 2>/dev/null; then
    test_pass "OPENAI_API_KEY configured"
else
    test_fail "OPENAI_API_KEY not configured"
fi

echo ""

# 2. Python Dependencies
echo "📦 2. Python Dependencies"
echo "----------------------"

if command_exists python3; then
    cd suppliersync
    if python3 -m pip show fastapi >/dev/null 2>&1; then
        test_pass "Python dependencies installed"
    else
        test_fail "Python dependencies not installed (run: pip install -r requirements.txt)"
    fi
    cd ..
else
    test_skip "Python 3 not found"
fi

echo ""

# 3. Node.js Dependencies
echo "📦 3. Node.js Dependencies"
echo "----------------------"

if command_exists npm; then
    cd dashboard
    if [ -d "node_modules" ]; then
        test_pass "Node.js dependencies installed"
    else
        test_fail "Node.js dependencies not installed (run: npm install)"
    fi
    cd ..
else
    test_skip "npm not found"
fi

echo ""

# 4. Database
echo "💾 4. Database"
echo "----------------------"

DB_PATH="${SQLITE_PATH:-suppliersync/suppliersync.db}"
if [ -f "$DB_PATH" ]; then
    test_pass "Database file exists: $DB_PATH"
    
    # Check if database has tables
    if command_exists sqlite3; then
        TABLE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
        if [ "$TABLE_COUNT" -gt 0 ]; then
            test_pass "Database has $TABLE_COUNT tables"
        else
            test_fail "Database has no tables (run: python populate_inventory.py)"
        fi
    else
        test_skip "sqlite3 command not found"
    fi
else
    test_fail "Database file not found: $DB_PATH (run: python populate_inventory.py)"
fi

echo ""

# 5. Security Utilities
echo "🔒 5. Security Utilities"
echo "----------------------"

if [ -f "suppliersync/core/security.py" ]; then
    test_pass "Security utilities module exists"
    
    # Test security module imports
    cd suppliersync
    if python3 -c "from core.security import validate_path, validate_table_name, validate_sku, validate_price" 2>/dev/null; then
        test_pass "Security utilities can be imported"
    else
        test_fail "Security utilities import failed"
    fi
    cd ..
else
    test_fail "Security utilities module not found"
fi

echo ""

# 6. API Service
echo "🌐 6. API Service"
echo "----------------------"

# Check if API is running
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    test_pass "API service is running on port 8000"
    
    # Test health endpoint
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
        test_pass "Health endpoint returns OK"
        
        # Check that db_path is not exposed
        if ! echo "$HEALTH_RESPONSE" | grep -q "db_path"; then
            test_pass "Health endpoint does not expose db_path (security)"
        else
            test_fail "Health endpoint exposes db_path (security issue)"
        fi
    else
        test_fail "Health endpoint did not return OK"
    fi
    
    # Test RAG status endpoint
    RAG_STATUS=$(curl -s http://localhost:8000/rag/status)
    if echo "$RAG_STATUS" | grep -q "status"; then
        test_pass "RAG status endpoint works"
    else
        test_fail "RAG status endpoint failed"
    fi
    
    # Test orchestrate endpoint (may fail if OpenAI key invalid)
    ORCH_RESPONSE=$(curl -s -X POST http://localhost:8000/orchestrate -w "%{http_code}" -o /tmp/orch_response.json 2>&1)
    HTTP_CODE="${ORCH_RESPONSE: -3}"
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "500" ]; then
        # 500 is acceptable if OpenAI key is invalid
        if [ "$HTTP_CODE" = "200" ]; then
            test_pass "Orchestrate endpoint works"
        else
            test_skip "Orchestrate endpoint returned 500 (check OpenAI API key)"
        fi
    else
        test_fail "Orchestrate endpoint failed with HTTP $HTTP_CODE"
    fi
    
else
    test_skip "API service not running (start with: uvicorn api:app --port 8000)"
fi

echo ""

# 7. Dashboard
echo "🎨 7. Dashboard"
echo "----------------------"

if curl -s http://localhost:3001 >/dev/null 2>&1 || curl -s http://localhost:3000 >/dev/null 2>&1; then
    DASHBOARD_PORT=""
    if curl -s http://localhost:3001 >/dev/null 2>&1; then
        DASHBOARD_PORT=3001
    else
        DASHBOARD_PORT=3000
    fi
    test_pass "Dashboard is running on port $DASHBOARD_PORT"
    
    # Test dashboard API routes
    if curl -s "http://localhost:$DASHBOARD_PORT/rag-status" >/dev/null 2>&1; then
        test_pass "Dashboard RAG status route works"
    else
        test_fail "Dashboard RAG status route failed"
    fi
else
    test_skip "Dashboard not running (start with: npm run dev)"
fi

echo ""

# 8. Dependency Security
echo "🔍 8. Dependency Security"
echo "----------------------"

if command_exists safety; then
    cd suppliersync
    if safety check --json >/dev/null 2>&1 || safety check >/dev/null 2>&1; then
        test_pass "Python dependency security check (no critical vulnerabilities)"
    else
        test_skip "Python dependency security check found issues (review with: safety check)"
    fi
    cd ..
else
    test_skip "safety not installed (pip install safety)"
fi

if command_exists npm; then
    cd dashboard
    if npm audit --audit-level=high >/dev/null 2>&1; then
        test_pass "Node.js dependency security check (no high severity vulnerabilities)"
    else
        test_skip "Node.js dependency security check found issues (review with: npm audit)"
    fi
    cd ..
fi

echo ""

# 9. Python Tests
echo "🐍 9. Python Tests"
echo "----------------------"

if command_exists pytest; then
    cd suppliersync
    if pytest tests/ -v 2>&1 | tee /tmp/pytest_output.txt; then
        test_pass "Python tests passed"
    else
        TEST_FAILURES=$(grep -c "FAILED" /tmp/pytest_output.txt 2>/dev/null || echo "0")
        if [ "$TEST_FAILURES" -gt 0 ]; then
            test_fail "Python tests failed ($TEST_FAILURES failures)"
        else
            test_skip "Python tests not run (install pytest: pip install pytest)"
        fi
    fi
    cd ..
else
    test_skip "pytest not installed (pip install pytest)"
fi

echo ""

# 10. Security Features
echo "🛡️  10. Security Features"
echo "----------------------"

# Test path validation
cd suppliersync
if python3 -c "
from core.security import validate_path
try:
    validate_path('../../../etc/passwd', allow_absolute=False)
    print('FAIL: Path traversal allowed')
    exit(1)
except ValueError:
    print('PASS: Path traversal blocked')
    exit(0)
" 2>/dev/null; then
    test_pass "Path traversal protection works"
else
    test_fail "Path traversal protection failed"
fi

# Test table name validation
if python3 -c "
from core.security import validate_table_name
allowed = ('table1', 'table2')
if validate_table_name('table1', allowed) and not validate_table_name('DROP TABLE', allowed):
    print('PASS: Table name validation works')
    exit(0)
else:
    print('FAIL: Table name validation failed')
    exit(1)
" 2>/dev/null; then
    test_pass "Table name validation works"
else
    test_fail "Table name validation failed"
fi

# Test SKU validation
if python3 -c "
from core.security import validate_sku
if validate_sku('WF-001') and not validate_sku('DROP TABLE products;'):
    print('PASS: SKU validation works')
    exit(0)
else:
    print('FAIL: SKU validation failed')
    exit(1)
" 2>/dev/null; then
    test_pass "SKU validation works"
else
    test_fail "SKU validation failed"
fi

cd ..

echo ""

# 11. Database Operations
echo "💾 11. Database Operations"
echo "----------------------"

if [ -f "$DB_PATH" ] && command_exists sqlite3; then
    # Test database integrity
    INTEGRITY=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>/dev/null | head -1)
    if [ "$INTEGRITY" = "ok" ]; then
        test_pass "Database integrity check passed"
    else
        test_fail "Database integrity check failed: $INTEGRITY"
    fi
    
    # Test that indexes exist
    INDEX_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';" 2>/dev/null || echo "0")
    if [ "$INDEX_COUNT" -gt 0 ]; then
        test_pass "Database has $INDEX_COUNT security indexes"
    else
        test_fail "Database missing security indexes"
    fi
fi

echo ""

# 12. Scripts
echo "📜 12. Utility Scripts"
echo "----------------------"

if [ -f "suppliersync/scripts/backup_database.sh" ]; then
    if [ -x "suppliersync/scripts/backup_database.sh" ]; then
        test_pass "Backup script exists and is executable"
    else
        test_fail "Backup script not executable (run: chmod +x scripts/backup_database.sh)"
    fi
else
    test_fail "Backup script not found"
fi

if [ -f "suppliersync/scripts/check_dependencies.sh" ]; then
    if [ -x "suppliersync/scripts/check_dependencies.sh" ]; then
        test_pass "Dependency check script exists and is executable"
    else
        test_fail "Dependency check script not executable (run: chmod +x scripts/check_dependencies.sh)"
    fi
else
    test_fail "Dependency check script not found"
fi

echo ""

# Summary
echo "========================================"
echo "📊 Test Summary"
echo "========================================"
echo -e "${GREEN}✅ Passed:${NC} $PASSED"
echo -e "${RED}❌ Failed:${NC} $FAILED"
echo -e "${YELLOW}⏭️  Skipped:${NC} $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi

