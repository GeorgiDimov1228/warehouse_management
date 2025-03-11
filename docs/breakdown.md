# Warehouse Management System File Breakdown

## Core Application Files

- **run.py**: The entry point that starts the entire application. It handles command-line options and environment setup.

- **app/\_\_init\_\_.py**: Creates and configures the application, connecting all the pieces together. It sets up logging, databases, and starts background services.

- **app/config.py**: Contains all configuration settings for different environments (development, testing, production). This is where system-wide settings are defined.

## Database Models

These files define how data is organized and stored:

- **app/models/user.py**: Manages user accounts and roles (admin, regular user, operator).

- **app/models/product.py**: Defines products with properties like name, barcode, RFID tag, and quantity.

- **app/models/category.py**: Organizes products into categories for better inventory management.

- **app/models/cabinet.py**: Defines physical storage units (cabinets and shelves) where products are placed.

- **app/models/transaction.py**: Records all movement of products (additions, removals, transfers).

## Key Features and Routes

Routes are the different screens and functions available in the system:

- **app/routes/auth.py**: Handles user login, logout, and registration.

- **app/routes/product.py**: Manages adding, editing, and viewing products. Also includes the main dashboard.

- **app/routes/category.py**: Handles product categorization.

- **app/routes/cabinet.py**: Manages physical storage locations including shelves and cabinet organization.

- **app/routes/rfid.py**: Core RFID functionality for tracking product movement.

- **app/routes/rfid_extended.py**: Additional RFID features like tag printing and history viewing.

- **app/routes/opcua.py**: Connects to industrial equipment like traffic lights and control panels.

## Services (Background Functionality)

- **app/services/rfid_listener.py**: Constantly monitors RFID readers for real-time updates when products move.

- **app/services/rfid_service.py**: Core logic for RFID tag handling, printing, and scanning.

- **app/services/opcua_service.py**: Connects to industrial equipment using the OPC UA protocol.

- **app/services/database.py**: Initializes the database and creates default settings.

- **app/services/backup_service.py**: Automatically backs up data at regular intervals.

## Deployment Files

- **Dockerfile**: Instructions for building the Docker container version.

- **docker-compose.yml**: Configuration for running multiple containers together (app, database, web server).

- **warehouse.service**: For installing as a traditional service on Linux/Ubuntu servers.

- **gunicorn_config.py**: Settings for the production web server.

- **nginx/conf/warehouse.conf**: Configuration for the web server that handles internet traffic.

## Documentation

- **README.md**: Overview of the system, features, and installation instructions.

- **docs/deployement.md**: Explains the two deployment options (Docker vs. traditional installation).

## Key Selling Points

1. **Real-time RFID Tracking**: The system constantly monitors inventory movement using RFID readers, updating the database instantly when products move.

2. **Flexible Storage Organization**: Cabinets and shelves can be configured with specific category permissions - either single-category (each shelf only accepts one product type) or multi-category.

3. **Industrial Integration**: Connects directly to warehouse equipment like traffic lights, PLCs, and HMI displays.

4. **Comprehensive Security**: Role-based access control ensures employees only access appropriate functions.

5. **Complete Transaction History**: Every movement is logged with timestamps and user information for full accountability.

6. **Multiple Deployment Options**: Can be installed using modern Docker containers or traditional server deployment based on customer preference.

7. **Real-time Alerts**: The system can notify administrators of irregular activity or equipment issues.

8. **Automatic Backups**: Data is automatically backed up on a configurable schedule to prevent data loss.