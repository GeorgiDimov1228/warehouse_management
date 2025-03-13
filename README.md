# Warehouse Management System

A Flask-based warehouse management system with OPC UA integration for industrial automation and RFID tracking capabilities.

## Features

- Product inventory management with categories
- Cabinet and shelf organization
- RFID tracking for products and user authentication
- OPC UA integration for industrial automation
- Automated database backups
- User authentication and role-based access
- Transaction history logging

## Prerequisites

- Python 3.8+ installed
- SQLite (included with Python)
- OPC UA server (for testing)

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
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
   - The default configuration is in the `.env` file
   - Modify as needed for your environment

### Option 2: Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
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

To initialize the database manually:
```bash
flask shell
```

Then in the shell:
```python
from app.services.database import initialize_database
initialize_database()
exit()
```

## Running the Application

### Option 1: Local Run
1. Start the application:
```bash
flask run
```

2. Navigate to `http://localhost:5000` in your web browser
   - For the health check endpoint: `http://localhost:5000/health`
   - For login: `http://localhost:5000/auth/login`

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
   - For login: `http://localhost:5000/auth/login`

## Testing the OPC UA Integration

The application includes an OPC UA server and client for testing:

1. Verify the OPC UA server is running:
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

## RFID Testing

For testing RFID functionality:

1. Authenticate a user with RFID:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"rfid_tag":"your_rfid_tag"}' http://localhost:5000/rfid/auth
```

2. Load items using RFID:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"rfid_tag":"user_rfid_tag", "product_rfid":"product_rfid_tag", "quantity":1, "shelf_id":1}' http://localhost:5000/rfid/load
```

3. Get items using RFID:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"rfid_tag":"user_rfid_tag", "product_id":1, "quantity":1, "shelf_id":1}' http://localhost:5000/rfid/get
```

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

## Automated Backups

The application automatically performs database backups according to the interval specified in the `.env` file. By default, backups are created every 24 hours in the `backups` directory.

## Architecture

The application follows a modular architecture:

- `app/__init__.py` - Application factory
- `app/config.py` - Configuration settings
- `app/models/` - Database models
- `app/routes/` - Route handlers
- `app/services/` - Service modules for OPC UA, database, backups
- `run.py` - Entry point to run the application

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
docker compose exec warehouse_management-webapp-1 python3 init_db.py

docker exec -it warehouse_management-webapp-1 python3 init_db.py
docker exec -it warehouse_management-webapp-1 python3 quick_test.py


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
If you encounter dependency issues like the `url_quote` error with newer Python versions:
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
- Without Docker: Check the log file defined in `.env` (default: `warehouse_log.log`)
- Set the log level in `app/__init__.py`

### Docker-Specific Issues
- If the container fails to start, check the logs: `docker-compose logs -f`
- To restart the container: `docker-compose restart`
- To rebuild the container after changes: `docker-compose up -d --build`
- To completely reset (removes volumes): `docker-compose down -v && docker-compose up -d`
