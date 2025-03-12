import pytest
import time
import concurrent.futures
from sqlalchemy.sql import text

def test_api_response_time(authenticated_client, test_products):
    """Test API endpoint response time."""
    # Define endpoints to test
    endpoints = [
        '/products/api/list',
        '/categories/api/list',
        '/cabinets/api/list',
        '/opcua/status',
        '/opcua/get-item-count'
    ]
    
    results = {}
    
    for endpoint in endpoints:
        start_time = time.time()
        response = authenticated_client.get(endpoint)
        end_time = time.time()
        
        response_time = end_time - start_time
        results[endpoint] = {
            'status_code': response.status_code,
            'response_time': response_time
        }
        
        # Assert each endpoint responds in less than 500ms
        # Note: This threshold might need adjustment based on your system
        assert response_time < 0.5, f"Endpoint {endpoint} took too long to respond: {response_time}s"
        assert response.status_code == 200
    
    return results

def test_dashboard_load_time(authenticated_client):
    """Test dashboard page load time."""
    start_time = time.time()
    response = authenticated_client.get('/products/dashboard')
    end_time = time.time()
    
    response_time = end_time - start_time
    
    # Dashboard may take a bit longer to generate
    assert response_time < 1.0, f"Dashboard took too long to load: {response_time}s"
    assert response.status_code == 200

def test_database_query_performance(app, test_products, test_categories):
    """Test database query performance."""
    with app.app_context():
        from app.models import db
        
        # Test a simple query
        start_time = time.time()
        products = db.session.execute(text("SELECT * FROM products")).fetchall()
        simple_query_time = time.time() - start_time
        
        # Test a join query
        start_time = time.time()
        product_categories = db.session.execute(text("""
            SELECT p.id, p.name, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
        """)).fetchall()
        join_query_time = time.time() - start_time
        
        # Reasonable thresholds for SQLite in memory
        assert simple_query_time < 0.01, f"Simple query took too long: {simple_query_time}s"
        assert join_query_time < 0.02, f"Join query took too long: {join_query_time}s"

def test_concurrent_requests(authenticated_client, test_products):
    """Test system under concurrent load."""
    # Define a list of endpoints to test
    endpoints = [
        '/products/dashboard',
        '/products/',
        '/categories/',
        '/cabinets/',
        '/products/api/list'
    ]
    
    # Create a list of requests to make
    requests = []
    for _ in range(3):  # Repeat each endpoint 3 times
        requests.extend(endpoints)
    
    def make_request(endpoint):
        start_time = time.time()
        response = authenticated_client.get(endpoint)
        end_time = time.time()
        return {
            'endpoint': endpoint,
            'status_code': response.status_code,
            'response_time': end_time - start_time
        }
    
    # Execute requests concurrently
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_endpoint = {executor.submit(make_request, endpoint): endpoint for endpoint in requests}
        for future in concurrent.futures.as_completed(future_to_endpoint):
            result = future.result()
            results.append(result)
    
    # Verify all requests succeeded
    for result in results:
        assert result['status_code'] == 200, f"Request to {result['endpoint']} failed with status {result['status_code']}"
    
    # Calculate some statistics
    total_time = sum(result['response_time'] for result in results)
    avg_time = total_time / len(results)
    max_time = max(result['response_time'] for result in results)
    
    # These thresholds might need adjustment
    assert avg_time < 0.5, f"Average response time too high: {avg_time}s"
    assert max_time < 1.0, f"Maximum response time too high: {max_time}s"

def test_product_creation_performance(app, test_categories):
    """Test performance of bulk product creation."""
    with app.app_context():
        from app.models import db
        from app.models.product import Product
        
        category_id = test_categories[0].id
        
        # Prepare a batch of products
        products = []
        for i in range(100):
            products.append(Product(
                name=f'Performance Test Product {i}',
                barcode=f'PERF-{i:03d}',
                rfid_tag=f'perf-rfid-{i:03d}',
                quantity=i,
                category_id=category_id
            ))
        
        # Measure time to bulk insert
        start_time = time.time()
        db.session.add_all(products)
        db.session.commit()
        bulk_insert_time = time.time() - start_time
        
        # Adjust threshold based on your system's capabilities
        assert bulk_insert_time < 0.5, f"Bulk insert took too long: {bulk_insert_time}s"
        
        # Measure query time after insert
        start_time = time.time()
        count = Product.query.count()
        query_time = time.time() - start_time
        
        assert count >= 100
        assert query_time < 0.01, f"Count query took too long: {query_time}s"