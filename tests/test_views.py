import pytest

def test_index_redirect(client):
    """Test that the index route redirects to login when not authenticated."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'<title>Login - Warehouse Management System</title>' in response.data

def test_register_page(client):
    """Test that the register page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'<title>Register - Warehouse Management System</title>' in response.data

def test_login_success(client, test_admin):
    """Test successful login."""
    response = client.post(
        '/auth/login',
        data={
            'username': test_admin.username,
            'password': 'testpass'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    # Should redirect to dashboard
    assert b'Dashboard' in response.data

def test_login_failure(client):
    """Test failed login."""
    response = client.post(
        '/auth/login',
        data={
            'username': 'wronguser',
            'password': 'wrongpass'
        }
    )
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_dashboard_authenticated(authenticated_client, test_products, test_categories):
    """Test dashboard access when authenticated."""
    response = authenticated_client.get('/products/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    assert b'Total Products' in response.data

def test_dashboard_unauthenticated(client):
    """Test dashboard access when not authenticated."""
    response = client.get('/products/dashboard')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_products_page(authenticated_client, test_products):
    """Test products page loads correctly."""
    response = authenticated_client.get('/products/')
    assert response.status_code == 200
    assert b'Products' in response.data
    # Check for one of our test products
    assert bytes(test_products[0].name, 'utf-8') in response.data

def test_categories_page(authenticated_client, test_categories):
    """Test categories page loads correctly."""
    response = authenticated_client.get('/categories/')
    assert response.status_code == 200
    assert b'Categories' in response.data
    # Check for one of our test categories
    assert bytes(test_categories[0].name, 'utf-8') in response.data

def test_cabinets_page(authenticated_client, test_cabinet):
    """Test cabinets page loads correctly."""
    response = authenticated_client.get('/cabinets/')
    assert response.status_code == 200
    assert b'Cabinets' in response.data
    # Check for our test cabinet
    assert bytes(test_cabinet.name, 'utf-8') in response.data

def test_add_product_page(authenticated_client, test_categories):
    """Test add product page loads correctly."""
    response = authenticated_client.get('/products/add')
    assert response.status_code == 200
    assert b'Add Product' in response.data
    # Check for category options
    for category in test_categories:
        assert bytes(category.name, 'utf-8') in response.data

def test_add_product_submission(authenticated_client, test_categories, app):
    """Test adding a new product."""
    category_id = test_categories[0].id
    response = authenticated_client.post(
        '/products/add',
        data={
            'name': 'New Test Product',
            'barcode': 'NEW-TEST-001',
            'rfid_tag': 'new-test-rfid-001',
            'category_id': category_id,
            'quantity': 15
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'New Test Product' in response.data
    
    # Verify in database
    with app.app_context():
        from app.models.product import Product
        product = Product.query.filter_by(barcode='NEW-TEST-001').first()
        assert product is not None
        assert product.name == 'New Test Product'
        assert product.quantity == 15

def test_edit_product(authenticated_client, test_products, app):
    """Test editing a product."""
    product = test_products[0]
    response = authenticated_client.post(
        f'/products/edit/{product.id}',
        data={
            'name': f'{product.name} Updated',
            'barcode': product.barcode,
            'rfid_tag': product.rfid_tag,
            'category_id': product.category_id,
            'quantity': product.quantity + 5
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert bytes(f'{product.name} Updated', 'utf-8') in response.data
    
    # Verify in database
    with app.app_context():
        from app.models.product import Product
        updated_product = Product.query.get(product.id)
        assert updated_product.name == f'{product.name} Updated'
        assert updated_product.quantity == product.quantity + 5

def test_delete_product(authenticated_client, test_products, app):
    """Test deleting a product."""
    product = test_products[0]
    response = authenticated_client.post(
        f'/products/delete/{product.id}',
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Verify product is deleted
    with app.app_context():
        from app.models.product import Product
        deleted_product = Product.query.get(product.id)
        assert deleted_product is None

def test_add_category(authenticated_client, app):
    """Test adding a new category."""
    response = authenticated_client.post(
        '/categories/add',
        data={
            'name': 'New Test Category',
            'description': 'This is a test category'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'New Test Category' in response.data
    
    # Verify in database
    with app.app_context():
        from app.models.category import Category
        category = Category.query.filter_by(name='New Test Category').first()
        assert category is not None
        assert category.description == 'This is a test category'

def test_add_cabinet(authenticated_client, app):
    """Test adding a new cabinet."""
    response = authenticated_client.post(
        '/cabinets/add',
        data={
            'name': 'New Test Cabinet',
            'category_mode': 'multi'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'New Test Cabinet' in response.data
    
    # Verify in database
    with app.app_context():
        from app.models.cabinet import Cabinet
        cabinet = Cabinet.query.filter_by(name='New Test Cabinet').first()
        assert cabinet is not None
        assert cabinet.category_mode == 'multi'

def test_cabinet_shelves(authenticated_client, test_cabinet, test_shelf):
    """Test viewing shelves for a cabinet."""
    response = authenticated_client.get(f'/cabinets/shelves/{test_cabinet.id}')
    assert response.status_code == 200
    assert bytes(test_cabinet.name, 'utf-8') in response.data
    assert bytes(test_shelf.name, 'utf-8') in response.data

def test_logout(authenticated_client):
    """Test logout functionality."""
    response = authenticated_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    
    # Try accessing a protected page after logout
    response = authenticated_client.get('/products/dashboard')
    assert response.status_code == 302
    assert '/auth/login' in response.location