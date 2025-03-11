# Docker Setup Instructions

This guide provides detailed steps for setting up and testing the Warehouse Management System using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Setup Steps

1. **Clone the repository and navigate to the project directory**

   ```bash
   git clone <repository-url>
   cd warehouse-management-system
   ```

2. **Build and start the Docker containers**

   ```bash
   docker-compose up -d
   ```

   This command will:
   - Build the Docker image with Python 3.8
   - Install all required dependencies
   - Start the Flask application
   - Map port 5000 to your local machine for the web server
   - Map port 4840 for the OPC UA server

3. **Initialize the database with test data**

   ```bash
   docker compose exec webapp python init_db.py
   ```

   This will create:
   - Default roles (admin, user, operator)
   - Test users (admin/admin123, operator/operator123)
   - Test categories, cabinets, shelves, and products

## Verifying the Setup

1. **Check if the container is running**

   ```bash
   docker-compose ps
   ```

   You should see the webapp container running.

2. **View application logs**

   ```bash
   docker-compose logs -f
   ```

3. **Test the health endpoint**

   ```bash
   curl http://localhost:5000/health
   ```

   Expected response: `{"status":"healthy"}`

4. **Test the OPC UA connection**

   ```bash
   curl http://localhost:5000/opcua/status
   ```

   Expected response: `{"status":"Connected"}`

## Testing the Application

1. **Access the application in your browser**
   
   Open http://localhost:5000/auth/login

2. **Log in with the test credentials**
   
   Username: `admin`
   Password: `admin123`

3. **Test the dashboard**
   
   Navigate to http://localhost:5000/products/dashboard

4. **Test the RFID API**

   ```bash
   # Authenticate with RFID
   curl -X POST -H "Content-Type: application/json" \
     -d '{"rfid_tag":"admin-rfid-001"}' \
     http://localhost:5000/rfid/auth
   ```

## Stopping and Cleaning Up

1. **Stop the Docker containers**

   ```bash
   docker-compose down
   ```

2. **Remove volumes if needed (this will delete your data)**

   ```bash
   docker-compose down -v
   ```

## Troubleshooting

1. **If the application fails to start**
   
   Check the logs:
   ```bash
   docker-compose logs -f
   ```

2. **If you need to rebuild the container**

   ```bash
   docker-compose up -d --build
   ```

3. **If the OPC UA server connection fails**

   Ensure ports are correctly mapped:
   ```bash
   docker-compose ps
   ```
   
   Check the OPC UA service logs:
   ```bash
   docker-compose logs -f | grep "OPC UA"
   ```

4. **To restart the application**

   ```bash
   docker-compose restart
   ```

5. **To access the Flask shell**

   ```bash
   docker-compose exec webapp flask shell
   ```

6. **To execute Python code directly**

   ```bash
   docker-compose exec webapp python -c "from app import create_app; app = create_app(); print('Flask app created')"
   ```

## Working with the Database

1. **Access the SQLite database**

   ```bash
   docker-compose exec webapp sqlite3 database.db
   ```

2. **Reset the database if needed**

   ```bash
   docker compose exec webapp python -c "from app.services.database import reset_database; from app import create_app; app = create_app(); with app.app_context(): reset_database()"
   ```

3. **Backup the database manually**

   ```bash
   docker-compose exec webapp python -c "from app.services.backup_service import backup_database; from app import create_app; app = create_app(); with app.app_context(): backup_database()"
   ```

