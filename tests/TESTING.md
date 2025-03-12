# Testing Guide for Warehouse Management System

This guide explains how to run the tests for the Warehouse Management System and describes the test suite structure.

## Prerequisites

Before running tests, make sure you have the following installed:

- Python 3.8 or higher
- pytest
- pytest-cov (for coverage reporting)

You can install the test dependencies with:

```bash
pip install pytest pytest-cov
```

## Running Tests

### Using the run_tests.py Script

The easiest way to run tests is using the provided `run_tests.py` script:

```bash
# Run all tests
python3 run_tests.py

# Run tests with verbose output
python3 run_tests.py -v

# Run tests with coverage reporting
python3 run_tests.py -c

# Run a specific test file
python3 run_tests.py -f tests/test_models.py

# Pass additional arguments to pytest
python3 run_tests.py -- -k "test_product"
```

### Running Tests Directly with pytest

You can also run tests directly with pytest:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run with coverage reporting
pytest --cov=app --cov-report=term --cov-report=html

# Run a specific test file
pytest tests/test_models.py

# Run tests matching a specific pattern
pytest -k "product"

# Run a specific test
pytest tests/test_models.py::test_product_creation
```

### Running Tests in Docker

If you're using Docker, you can run the tests inside the container:

```bash
# Run all tests
docker compose exec webapp python run_tests.py

# Run specific tests
docker compose exec webapp python run_tests.py -f tests/test_models.py -v
```

## Test Suite Structure

The test suite is organized into several files, each focusing on a specific aspect of the system:

1. **test_models.py**: Tests the database models and their relationships
2. **test_api.py**: Tests the API endpoints
3. **test_views.py**: Tests the web views and UI functionality
4. **test_rfid.py**: Tests the RFID service and related functionality
5. **test_opcua.py**: Tests the OPC UA service for industrial equipment integration
6. **test_performance.py**: Tests system performance and response times
7. **test_config.py**: Tests configuration loading and environment variables

The test fixtures are defined in **conftest.py**, which provides common test data and setup code shared across tests.

## Test Coverage

To see the test coverage report, run:

```bash
python run_tests.py -c
```

This will generate an HTML coverage report in the `htmlcov` directory. Open `htmlcov/index.html` in your web browser to view detailed coverage information.

## Writing New Tests

When adding new functionality to the system, you should also add tests for that functionality. Follow these guidelines:

1. **Choose the right test file**: Add your test to the appropriate file based on what you're testing (models, API, views, etc.)
2. **Use fixtures**: Leverage existing fixtures from conftest.py when possible
3. **Follow the naming convention**: Prefix test functions with `test_`
4. **Include assertions**: Make sure your test includes assertions to verify expected behavior

Example of a new test:

```python
def test_new_feature(app, authenticated_client):
    """Test the new feature functionality."""
    # Setup
    # ...
    
    # Execute
    response = authenticated_client.get('/new-feature')
    
    # Assert
    assert response.status_code == 200
    assert b'expected content' in response.data
```

## Continuous Integration

For automated CI/CD pipelines, you can use the following command to run all tests:

```bash
python run_tests.py -c --junit-xml=test-results.xml
```

This will generate a JUnit XML report that can be consumed by CI systems like Jenkins, GitLab CI, or GitHub Actions.

## Troubleshooting Tests

If you encounter issues with tests:

1. **Run with verbose output**: Use `-v` to see more detailed test output
2. **Run specific tests**: Isolate the failing test with `-k` or by specifying the test file
3. **Check logs**: Look for error messages in the test output
4. **Database issues**: Verify that the database is properly initialized in the test environment
5. **Environment variables**: Ensure all required environment variables are set correctly

If tests are failing in the Docker environment but passing locally, check for differences in the Python version or installed packages.

## Performance Testing Considerations

The performance tests in `test_performance.py` include thresholds that may need to be adjusted based on your specific environment. These tests are designed to catch regressions in performance but may need tuning to avoid false failures in different environments.

If performance tests are failing but functional tests pass, you can:

1. Adjust the thresholds in the tests
2. Skip performance tests during regular development with `pytest -k "not test_performance"`
3. Run performance tests separately in a controlled environment