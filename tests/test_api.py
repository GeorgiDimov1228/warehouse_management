import pytest
import json

def test_product_api_list(authenticated_client, test_products):
    """Test the product API list endpoint."""
    response = authenticated_client.get('/products/api/list')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 3  # We created 3 test products
    
    # Check the structure of a product in the response
    product = data[0]
    assert 'id' in product
    assert 'name' in product
    assert 'barcode' in product
    assert 'rfid_tag' in product
    assert 'category_id' in product
    assert 'category_name' in product

def test_category_api_list(authenticated_client, test_categories):
    """Test the category API list endpoint."""
    response = authenticated_client.get('/categories/api/list')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 3  # We created 3 test categories
    
    # Check the structure of a category in the response
    category = data[0]
    assert 'id' in category
    assert 'name' in category
    assert 'description' in category

def test_cabinet_api_list(authenticated_client, test_cabinet):
    """Test the cabinet API list endpoint."""
    response = authenticated_client.get('/cabinets/api/list')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1  # At least our test cabinet
    
    # Check if our test cabinet is in the response
    cabinet_exists = False
    for cabinet in data:
        if cabinet['name'] == test_cabinet.name:
            cabinet_exists = True
            assert 'id' in cabinet
            assert 'category_mode' in cabinet
            assert 'shelves_count' in cabinet
    
    assert cabinet_exists, "Test cabinet not found in API response"

def test_opcua_status(authenticated_client):
    """Test the OPC UA status endpoint."""
    response = authenticated_client.get('/opcua/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

def test_rfid_auth(authenticated_client, test_admin):
    """Test the RFID authentication endpoint."""
    response = authenticated_client.post(
        '/rfid/auth',
        json={'rfid_tag': test_admin.rfid_tag}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user_id' in data
    assert data['user_id'] == test_admin.id
    assert data['username'] == test_admin.username

def test_rfid_auth_invalid(authenticated_client):
    """Test the RFID authentication endpoint with invalid tag."""
    response = authenticated_client.post(
        '/rfid/auth',
        json={'rfid_tag': 'non-existent-tag'}
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_rfid_load(authenticated_client, test_admin, test_products, test_shelf):
    """Test the RFID load endpoint."""
    product = test_products[0]
    initial_quantity = product.quantity
    
    response = authenticated_client.post(
        '/rfid/load',
        json={
            'rfid_tag': test_admin.rfid_tag,
            'product_rfid': product.rfid_tag,
            'quantity': 3,
            'shelf_id': test_shelf.id
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'new_quantity' in data
    assert data['new_quantity'] == initial_quantity + 3

def test_rfid_get(authenticated_client, test_admin, test_products, test_shelf, app):
    """Test the RFID get (retrieve) endpoint."""
    with app.app_context():
        product = test_products[0]
        initial_quantity = product.quantity
        
        response = authenticated_client.post(
            '/rfid/get',
            json={
                'rfid_tag': test_admin.rfid_tag,
                'product_id': product.id,
                'quantity': 2,
                'shelf_id': test_shelf.id
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'remaining_quantity' in data
        assert data['remaining_quantity'] == initial_quantity - 2

def test_opcua_item_count(authenticated_client, test_products):
    """Test the OPC UA item count endpoint."""
    response = authenticated_client.get('/opcua/get-item-count')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'item_count' in data
    
    # The item count should be the sum of all product quantities
    expected_total = sum(p.quantity for p in test_products)
    assert data['item_count'] == expected_total

def test_unauthenticated_api_access(client):
    """Test API access without authentication."""
    endpoints = [
        '/products/api/list',
        '/categories/api/list',
        '/cabinets/api/list'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [401, 302]  # Either unauthorized or redirect to login