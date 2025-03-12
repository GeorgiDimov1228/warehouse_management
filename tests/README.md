# Warehouse Management System Tests

This directory contains tests for the Warehouse Management System.

## Directory Structure

```
tests/
├── conftest.py             # Shared test fixtures and setup
├── test_models.py          # Tests for database models
├── test_api.py             # Tests for API endpoints
├── test_views.py           # Tests for web views and UI
├── test_rfid.py            # Tests for RFID functionality
├── test_opcua.py           # Tests for OPC UA integration
├── test_performance.py     # Tests for system performance
└── test_config.py          # Tests for configuration loading
```

## Quick Start

To run all tests:

```bash
cd /path/to/warehouse-management
pytest
```

To run a specific test file:

```bash
pytest tests/test_models.py

# To run all tests except RFID
pytest tests/test_models.py tests/test_views.py tests/test_api.py tests/test_config.py

# Or to skip specific test files
pytest --ignore=tests/test_rfid.py --ignore=tests/test_opcua.py
```

See the full [TESTING.md](../TESTING.md) guide for more options and details.

## Running in Docker

If you're using Docker:

```bash
docker compose exec warehouse_management-webapp-1  pytest

docker exec -it warehouse_management-webapp-1 bash
cd /app
pytest tests/test_models.py -v

docker exec -it warehouse_management-webapp-1 python run_tests.py -f tests/test_models.py -v

```

## Configuration

The tests use SQLite in-memory databases by default. This is configured in `conftest.py` with:

```python
app.config.update({
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'WTF_CSRF_ENABLED': False
})
```

## Available Fixtures

The most commonly used fixtures include:

- `app` - Flask application instance
- `client` - Flask test client
- `authenticated_client` - Flask test client with authenticated session
- `test_admin` - Admin user for testing
- `test_operator` - Operator user for testing
- `test_categories` - Test categories
- `test_products` - Test products
- `test_cabinet` - Test cabinet
- `test_shelf` - Test shelf

See `conftest.py` for the complete list of available fixtures.