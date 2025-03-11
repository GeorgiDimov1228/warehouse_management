#!/bin/bash

# Make sure we're in the project directory
cd "$(dirname "$0")"

# Create templates directory structure
mkdir -p app/templates/auth
mkdir -p app/templates/products
mkdir -p app/templates/categories
mkdir -p app/templates/cabinets

# Add template files - you need to create these files manually
# from the template contents provided earlier
echo "Creating template directory structure..."
echo "Please create the following template files:"
echo "- app/templates/auth/login.html"
echo "- app/templates/auth/register.html"
echo "- app/templates/products/dashboard.html"

# Rebuild Docker container
echo "Rebuilding Docker container..."
docker compose down
docker compose up -d --build

# Wait for container to start
echo "Waiting for container to start..."
sleep 5

# Initialize the database
echo "Initializing database..."
docker compose exec webapp python init_db.py

echo "Setup complete!"
echo "You can now access the application at: http://localhost:5000/auth/login"
echo "Login with: admin / admin123"
