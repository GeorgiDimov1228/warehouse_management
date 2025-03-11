# Warehouse Management System with RFID Integration

## Overview

A comprehensive warehouse management system with RFID tracking capabilities, designed for industrial warehouse environments. This system integrates with OPC UA for industrial automation control, RFID readers for real-time inventory tracking, and provides a complete solution for managing products, categories, cabinets, and shelves.

## Key Features

- **Real-time RFID Tracking**: Monitor inventory movement using RFID readers with WebSocket real-time updates
- **OPC UA Integration**: Control industrial automation equipment including traffic lights and PLCs
- **Product Management**: Comprehensive product catalog with categorization and barcode support
- **Shelf Organization**: Assign categories to cabinets and shelves for organized storage
- **User Authentication**: Secure access control with role-based permissions
- **Transaction Logging**: Complete history of all inventory movements with operator tracking (who took what, when, and how much)
- **Multiple Deployment Options**: Docker containers or traditional server deployment

## System Architecture

The system follows a modular architecture with clear separation of concerns:

- **Flask Web Application**: Core business logic and API endpoints
- **OPC UA Server/Client**: Industrial communication layer
- **RFID Services**: Real-time RFID reader communication and event processing
- **SQLAlchemy ORM**: Database abstraction for clean data access
- **Gunicorn/NGINX**: Production-ready web server configuration

## Technologies Used

- **Backend**: Flask, Python 3.9+
- **Database**: SQLite (development), PostgreSQL (production)
- **ORM**: SQLAlchemy, Flask-SQLAlchemy
- **Industrial Communication**: Python-OPCUA
- **RFID Communication**: WebSockets, HTTP APIs
- **Deployment**: Docker, Gunicorn, NGINX, Systemd
- **Security**: HTTPS, API key authentication

## Getting Started

### Prerequisites

- Python 3.9 or higher
- PostgreSQL (for production)
- Docker and Docker Compose (for container deployment)
- RFID readers and compatible hardware
- OPC UA compatible PLCs or industrial equipment

### Installation

#### Option 1: Docker Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/warehouse-management.git
   cd warehouse-management
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env.production
   # Edit .env.production with your specific configuration
   ```

3. Start the containers:
   ```bash
   docker-compose up -d
   ```

4. Access the application at http://localhost (or your configured domain)

#### Option 2: Traditional Server Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/warehouse-management.git
   cd warehouse-management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

5. Set up the database:
   ```bash
   flask db upgrade
   ```

6. Configure the systemd service:
   ```bash
   sudo cp warehouse.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable warehouse
   sudo systemctl start warehouse
   ```

7. Set up NGINX (optional):
   ```bash
   sudo cp nginx/conf/warehouse.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/warehouse.conf /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

## Usage

### RFID Tag Management

The system provides endpoints for RFID tag management:

- `/rfid-hardware/print-tag`: Print and encode new RFID tags
- `/rfid-hardware/batch-print`: Print multiple tags in batch
- `/rfid-hardware/simulate-scan`: Test the system without physical readers
- `/rfid-hardware/inventory`: List all RFID-tracked items
- `/rfid-hardware/tag-history/<rfid_tag>`: View history of specific tags

### Cabinet and Shelf Management

Cabinets and shelves can be configured with specific category permissions:

- Single-category mode: Each shelf accepts only one product category
- Multi-category mode: Shelves can store products from multiple categories

### Inventory Operations

- Scan RFID tags to automatically track inventory movement
- Assign products to appropriate shelves based on category rules
- Monitor inventory levels in real-time

## Configuration

The application is highly configurable through environment variables:

- Core application settings in `.env` or `.env.production`
- Advanced settings in `app/config.py`
- NGINX server configuration in `nginx/conf/warehouse.conf`
- Gunicorn settings in `gunicorn_config.py`

## Hardware Integration

### RFID Readers

The system supports both WebSocket and HTTP polling for RFID readers:

- WebSocket readers provide real-time event streaming
- HTTP polling is available for readers that don't support WebSockets
- Configure reader URLs and authentication in the environment variables

### OPC UA Industrial Equipment

Integration with industrial automation through OPC UA:

- Connect to PLCs, traffic lights, and other industrial equipment
- Control operations through the `/opcua/*` endpoints
- Monitor connection status via `/opcua/status`

## Security Considerations

- All production deployments should use HTTPS
- API keys must be kept secure and rotated regularly
- RFID simulation should be disabled in production
- Database backups should be encrypted and stored securely

## License

[Your License Here]

## Contributing

[Your Contribution Guidelines Here]