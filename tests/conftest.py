import pytest
from app import create_app
from app.models import db
from app.models.user import User, Role
from app.models.category import Category
from app.models.product import Product
from app.models.cabinet import Cabinet, Shelf
from app.models.transaction import Transaction, RFIDTracking

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False  # Disable CSRF for testing
    })
    
    # Create application context
    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        # Clean up after the test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def admin_role(app):
    """Create admin role."""
    with app.app_context():
        role = Role(role_name='admin')
        db.session.add(role)
        db.session.commit()
        return role

@pytest.fixture
def operator_role(app):
    """Create operator role."""
    with app.app_context():
        role = Role(role_name='operator')
        db.session.add(role)
        db.session.commit()
        return role

@pytest.fixture
def test_admin(app, admin_role):
    """Create a test admin user."""
    with app.app_context():
        user = User(
            username='testadmin',
            password='testpass',
            rfid_tag='test-rfid-admin'
        )
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_operator(app, operator_role):
    """Create a test operator user."""
    with app.app_context():
        user = User(
            username='testoperator',
            password='testpass',
            rfid_tag='test-rfid-operator'
        )
        user.roles.append(operator_role)
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_categories(app):
    """Create test categories."""
    with app.app_context():
        categories = [
            Category(name='Electronics', description='Electronic components and devices'),
            Category(name='Mechanical', description='Mechanical parts and tools'),
            Category(name='Consumables', description='Items that are consumed during production')
        ]
        db.session.add_all(categories)
        db.session.commit()
        return categories

@pytest.fixture
def test_cabinet(app):
    """Create a test cabinet."""
    with app.app_context():
        cabinet = Cabinet(name='Test Cabinet', category_mode='single')
        db.session.add(cabinet)
        db.session.commit()
        return cabinet

@pytest.fixture
def test_shelf(app, test_cabinet, test_categories):
    """Create a test shelf with a category."""
    with app.app_context():
        shelf = Shelf(
            name='Test Shelf', 
            cabinet_id=test_cabinet.id,
            allows_multiple_categories=False
        )
        shelf.categories.append(test_categories[0])  # Electronics category
        db.session.add(shelf)
        db.session.commit()
        return shelf

@pytest.fixture
def test_products(app, test_categories):
    """Create test products."""
    with app.app_context():
        products = [
            Product(
                name='Arduino Nano',
                barcode='TEST-ARD-001',
                rfid_tag='test-rfid-ard-001',
                quantity=10,
                category_id=test_categories[0].id  # Electronics
            ),
            Product(
                name='Wrench Set',
                barcode='TEST-TLS-001',
                rfid_tag='test-rfid-tls-001',
                quantity=5,
                category_id=test_categories[1].id  # Mechanical
            ),
            Product(
                name='Solder Wire',
                barcode='TEST-CON-001',
                rfid_tag='test-rfid-con-001',
                quantity=20,
                category_id=test_categories[2].id  # Consumables
            )
        ]
        db.session.add_all(products)
        db.session.commit()
        return products

@pytest.fixture
def test_transaction(app, test_products, test_admin, test_shelf):
    """Create a test transaction."""
    with app.app_context():
        transaction = Transaction(
            user_id=test_admin.id,
            product_id=test_products[0].id,
            quantity=2,
            transaction_type='move',
            shelf_id=test_shelf.id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

@pytest.fixture
def authenticated_client(client, test_admin):
    """A test client that's logged in as admin."""
    with client.session_transaction() as session:
        session['user_id'] = test_admin.id
        session['username'] = test_admin.username
    return client

@pytest.fixture
def operator_client(client, test_operator):
    """A test client that's logged in as operator."""
    with client.session_transaction() as session:
        session['user_id'] = test_operator.id
        session['username'] = test_operator.username
    return client