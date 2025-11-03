# Testing Guide

This guide covers testing procedures for SupplierSync.

## Overview

SupplierSync includes comprehensive testing across multiple layers:
- **Unit Tests** - Python pytest tests for core functionality
- **Integration Tests** - End-to-end API and database tests
- **Security Tests** - Security feature validation
- **Comprehensive Test Suite** - Full system validation

## Running Tests

### Quick Test (All Tests)

```bash
# From project root
./test_all.sh
```

This comprehensive test suite checks:
- Environment configuration
- Python and Node.js dependencies
- Database connectivity and integrity
- API service health and endpoints
- Dashboard connectivity
- Dependency security scanning
- Python unit tests
- Security features

### Python Unit Tests

```bash
# From suppliersync directory
cd suppliersync
pytest tests/ -v

# Run specific test file
pytest tests/test_governance.py -v

# Run specific test
pytest tests/test_governance.py::test_retail_below_wholesale -v
```

### Integration Tests

```bash
# From project root
./test_integration.sh
```

This tests:
- FastAPI health endpoint
- Database connectivity
- Orchestrate endpoint
- Dashboard server
- Environment configuration

## Test Coverage

### Python Tests

**Governance Tests** (`tests/test_governance.py`):
- ✅ Retail price below wholesale rejection
- ✅ Margin below minimum rejection
- ✅ Valid price approval
- ✅ Daily drift exceeded rejection
- ✅ Daily drift within limit approval
- ✅ Category blocked rejection
- ✅ Missing SKU rejection
- ✅ Invalid price format rejection

**Security Tests** (`tests/test_security.py`):
- ✅ Path traversal blocking
- ✅ Absolute path blocking
- ✅ Valid relative path handling
- ✅ Base directory validation
- ✅ Table name validation
- ✅ Filename sanitization
- ✅ SKU validation
- ✅ Price validation

**Database Tests** (`tests/test_database.py`):
- ✅ Database creation
- ✅ Read-only mode
- ✅ Database backup
- ✅ Database statistics
- ✅ Connection validation

**API Tests** (`tests/test_api.py`):
- ✅ Health check endpoint
- ✅ RAG status endpoint
- ✅ RAG rebuild endpoint
- ✅ Orchestrate endpoint
- ✅ Error message sanitization
- ✅ CORS headers

### Integration Tests

**API Service** (`test_integration.sh`):
- ✅ FastAPI health endpoint
- ✅ Database file existence
- ✅ Database connectivity
- ✅ Orchestrate endpoint
- ✅ Dashboard server
- ✅ Environment configuration

**Comprehensive** (`test_all.sh`):
- ✅ Environment check
- ✅ Python dependencies
- ✅ Node.js dependencies
- ✅ Database file and integrity
- ✅ Security utilities
- ✅ API service health and endpoints
- ✅ Dashboard connectivity
- ✅ Dependency security scanning
- ✅ Python unit tests
- ✅ Security features
- ✅ Database operations
- ✅ Utility scripts

## Test Requirements

### Python Dependencies

```bash
pip install -r requirements-test.txt
```

Includes:
- `pytest>=7.4.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `httpx>=0.27.0` - HTTP client for API tests

### Environment Setup

1. **API Service** - Must be running on port 8000:
   ```bash
   cd suppliersync
   uvicorn api:app --reload --port 8000
   ```

2. **Dashboard** - Must be running on port 3001 (or 3000):
   ```bash
   cd dashboard
   npm run dev
   ```

3. **Database** - Must exist and be initialized:
   ```bash
   cd suppliersync
   python populate_inventory.py
   ```

4. **Environment Variables** - Must be configured:
   - `suppliersync/.env` - Python service config
   - `dashboard/.env.local` - Next.js dashboard config

## Writing New Tests

### Python Test Structure

```python
import pytest
from core.module import function

class TestFeature:
    """Test feature description."""
    
    def test_basic_case(self):
        """Test basic functionality."""
        result = function(input)
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            function(invalid_input)
```

### Test Best Practices

1. **Test Naming**: Use descriptive names (`test_retail_below_wholesale`)
2. **Test Isolation**: Each test should be independent
3. **Test Data**: Use fixtures for shared test data
4. **Assertions**: Use clear assertions with helpful messages
5. **Coverage**: Test both success and failure cases

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Python dependencies
        run: |
          cd suppliersync
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Install Node.js dependencies
        run: |
          cd dashboard
          npm ci
      - name: Run Python tests
        run: |
          cd suppliersync
          pytest tests/ -v
      - name: Run integration tests
        run: |
          ./test_integration.sh
```

## Troubleshooting

### Common Issues

**Test Failures:**
- Check that services are running (API, Dashboard)
- Verify environment variables are set
- Ensure database is initialized
- Check Python and Node.js dependencies are installed

**Import Errors:**
- Verify `suppliersync` directory is in Python path
- Check `pytest.ini` configuration
- Ensure all dependencies are installed

**Database Errors:**
- Verify database file exists
- Check database permissions
- Ensure database is initialized

**API Errors:**
- Verify API service is running
- Check API port (default: 8000)
- Verify environment variables

**Dashboard Errors:**
- Verify dashboard is running
- Check dashboard port (default: 3001 or 3000)
- Verify environment variables

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Next.js Testing](https://nextjs.org/docs/testing)

