# Warehouse Management System

A Flask-based warehouse management system with OPC UA integration for industrial automation and RFID tracking capabilities.

## Features

- Product inventory management with categories
- Cabinet and shelf organization with category-based assignment
- RFID tracking for products and user authentication
- OPC UA integration for industrial PLC communication
- Automated database backups
- User authentication and role-based access (admin, operator, user)
- Transaction history logging
- Dashboard with real-time statistics
- HMI (Human-Machine Interface) for warehouse operations

## Prerequisites

- Python 3.8+ installed
- SQLite (included with Python)
- OPC UA server (for PLC connectivity testing)

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/Limoncho-san/warehouse_management.git
cd warehouse-management-system
```

2. Create and activate a virtual environment:
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env.example` to `.env` (or use the provided `.env` file)
   - Modify as needed for your environment, especially the PLC_OPC_UA_URL

### Option 2: Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/Limoncho-san/warehouse_management.git
cd warehouse-management-system
```

2. Build and start the Docker containers:
```bash
docker-compose up -d
```

This will:
- Build the Docker image with Python 3.8
- Install all required dependencies
- Set up environment variables
- Start the Flask application
- Map port 5000 to your local machine

## Database Setup

The application will automatically create the database and required tables on first run. 

To initialize the database with test data:
```bash
flask shell
```

Then in the shell:
```python
from app.services.database import initialize_database
initialize_database()
exit()
```

Or use the provided script:
```bash
python init_db.py
```

This will create:
- Default roles (admin, user, operator)
- Test users (admin/admin123, operator/operator123)
- Test categories, cabinets, shelves, and products

## Running the Application

### Option 1: Local Run
1. Start the application:
```bash
python run.py
# or
flask run
```

2. Navigate to `http://localhost:5000` in your web browser
   - For the health check endpoint: `http://localhost:5000/health`
   - For login: `http://localhost:5000/auth/login` (use admin/admin123)

### Option 2: Running with Docker (Recommended)
1. Start the application:
```bash
docker-compose up -d
```

2. Check if the container is running:
```bash
docker-compose ps
```

3. View application logs:
```bash
docker-compose logs -f
```

4. Navigate to `http://localhost:5000` in your web browser
   - For the health check endpoint: `http://localhost:5000/health`
   - For login: `http://localhost:5000/auth/login` (use admin/admin123)

## System Architecture

The application follows a modular architecture:

- `app/__init__.py` - Application factory
- `app/config.py` - Configuration settings
- `app/models/` - Database models (User, Product, Category, Cabinet, Shelf, Transaction)
- `app/routes/` - Route handlers for different sections (auth, product, category, cabinet, opcua, rfid)
- `app/services/` - Service modules (OPC UA client, database, backups)
- `app/templates/` - HTML templates for web interface
- `run.py` - Entry point to run the application

## Testing the OPC UA Integration

The application includes an OPC UA client for connecting to PLCs:

1. Verify the OPC UA server connection:
```bash
curl http://localhost:5000/opcua/status
```

2. Read a value from the OPC UA server:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"node_id":"ns=2;s=ItemCount"}' http://localhost:5000/opcua/read
```

3. Write a value to the OPC UA server:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"node_id":"ns=2;s=ItemCount", "value":100}' http://localhost:5000/opcua/write
```

4. Sync inventory with OPC UA:
```bash
curl -X POST http://localhost:5000/opcua/sync-inventory
```

## RFID Testing

For testing RFID functionality:

1. Authenticate a user with RFID:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"rfid_tag":"admin-rfid-001"}' http://localhost:5000/rfid/auth
```

2. Load items using RFID:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"rfid_tag":"admin-rfid-001", "product_rfid":"rfid-ard-001", "quantity":1, "shelf_id":1}' http://localhost:5000/rfid/load
```

3. Get items using RFID:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"rfid_tag":"admin-rfid-001", "product_id":1, "quantity":1, "shelf_id":1}' http://localhost:5000/rfid/get
```

## HMI Interface

The system includes an HMI (Human-Machine Interface) for warehouse operations:

1. Access the HMI at: `http://localhost:5000/hmi/`

Features include:
- Product scanning (barcode/RFID)
- Adding new products with optimal shelf placement
- Moving products between shelves
- Cabinet overview
- Transaction history

## API Endpoints

### Authentication
- `GET /auth/login` - Display login form
- `POST /auth/login` - Process login
- `GET /auth/logout` - Logout user
- `GET /auth/status` - Check login status
- `GET/POST /auth/register` - Register new user

### Products
- `GET /products/` - List all products
- `GET/POST /products/add` - Add new product
- `GET/POST /products/edit/<id>` - Edit product
- `POST /products/delete/<id>` - Delete product
- `GET /products/api/list` - API list of products
- `GET /products/dashboard` - Dashboard with statistics

### Categories
- `GET /categories/` - List all categories
- `GET/POST /categories/add` - Add new category
- `GET/POST /categories/edit/<id>` - Edit category
- `POST /categories/delete/<id>` - Delete category
- `GET /categories/api/list` - API list of categories

### Cabinets
- `GET /cabinets/` - List all cabinets
- `GET/POST /cabinets/add` - Add new cabinet
- `GET/POST /cabinets/edit/<id>` - Edit cabinet
- `POST /cabinets/delete/<id>` - Delete cabinet
- `GET /cabinets/shelves/<cabinet_id>` - List shelves for a cabinet
- `GET/POST /cabinets/shelves/add/<cabinet_id>` - Add shelf to cabinet
- `GET/POST /cabinets/shelves/edit/<shelf_id>` - Edit shelf
- `POST /cabinets/shelves/delete/<shelf_id>` - Delete shelf
- `POST /cabinets/traffic-light` - Control traffic light
- `GET /cabinets/api/list` - API list of cabinets

### OPC UA
- `GET /opcua/status` - Check OPC UA connection status
- `POST /opcua/read` - Read OPC UA value
- `POST /opcua/write` - Write OPC UA value
- `GET /opcua/get-item-count` - Get item count
- `POST /opcua/set-item-count` - Set item count
- `GET /opcua/get-traffic-light` - Get traffic light status
- `POST /opcua/set-traffic-light` - Set traffic light status
- `GET /opcua/get-hmi-status` - Get HMI status
- `POST /opcua/set-hmi-command` - Set HMI command
- `POST /opcua/update` - Update OPC UA node
- `POST /opcua/sync-inventory` - Sync inventory with OPC UA

### RFID
- `POST /rfid/auth` - Authenticate with RFID
- `POST /rfid/load` - Load items with RFID
- `POST /rfid/get` - Get items with RFID

### HMI
- `GET /hmi/` - Main HMI interface
- `POST /hmi/add-product` - Add a new product and get placement
- `POST /hmi/scan-product` - Scan a product by barcode or RFID
- `POST /hmi/move-product` - Move a product to a new location

## Automated Backups

The application automatically performs database backups according to the interval specified in the `.env` file. By default, backups are created every 24 hours in the `backups` directory.

You can manually trigger a backup with:

```python
from app.services.backup_service import backup_database
from app import create_app
app = create_app()
with app.app_context():
    backup_database()
```

## Running Tests

The system includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=app

# Run a specific test file
pytest tests/test_models.py

# Using the run_tests.py helper
python run_tests.py -v -c
```

### Docker Test Execution

```bash
docker compose exec webapp python run_tests.py
```

## Security Notes

For production deployment:
- Change the `FLASK_SECRET_KEY` in the `.env` file
- Implement proper password hashing (the current implementation stores passwords in plaintext)
- Set up HTTPS
- Configure proper database user permissions
- Restrict access to sensitive OPC UA nodes

## Troubleshooting

### Database Issues
If you encounter database issues, you can reset the database:

With Docker:
```bash
docker compose exec webapp python -c "from app.services.database import reset_database; from app import create_app; app = create_app(); with app.app_context(): reset_database()"
```

Without Docker:
```bash
# In a Python shell
from app.services.database import reset_database
from app import create_app
app = create_app()
with app.app_context():
    reset_database()
```

### Dependency Issues
If you encounter dependency issues:
- Use the Docker setup which uses Python 3.8
- If using local installation, create a virtual environment with Python 3.8:
  ```bash
  python3.8 -m venv venv
  ```

### OPC UA Connection Problems
- Verify the OPC UA server is running
- Check the endpoint configuration in `.env` or docker-compose.yml
- Verify no firewall is blocking the connection
- If using Docker, ensure the container has proper network access

### Logging
- With Docker: `docker-compose logs -f`
- Without Docker: Check the log file in the instance directory
- Adjust log level in `app/__init__.py` if needed

### Quick Test Script
To verify the application can be initialized correctly:
```bash
python quick_test.py
```

### Docker-Specific Issues
- If the container fails to start, check the logs: `docker-compose logs -f`
- To restart the container: `docker-compose restart`
- To rebuild the container after changes: `docker-compose up -d --build`
- To completely reset (removes volumes): `docker-compose down -v && docker-compose up -d`
