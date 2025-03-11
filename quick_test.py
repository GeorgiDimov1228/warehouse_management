#!/usr/bin/env python
"""
Quick test script to verify application configuration and imports.
Run this script to check if basic imports and Flask app creation work.
"""

import os
import sys

def test_app_creation():
    """Test if the Flask app can be created without errors"""
    print("Testing application imports and creation...")
    try:
        from app import create_app
        print("✓ Successfully imported create_app function")
        
        app = create_app()
        print("✓ Successfully created Flask application instance")
        
        print("\nApplication configuration:")
        for key in sorted(app.config.keys()):
            if not key.startswith('_'):
                print(f"  {key}: {app.config[key]}")
        
        print("\nRegistered blueprints:")
        for blueprint_name in app.blueprints:
            print(f"  {blueprint_name}: {app.blueprints[blueprint_name]}")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nTroubleshooting:")
        print("  - Check that your app directory is a proper Python package (contains __init__.py)")
        print("  - Ensure PYTHONPATH includes the project root directory")
        print("  - Verify there are no circular imports")
        return False
    except Exception as e:
        print(f"✗ Error creating app: {e}")
        print("\nTroubleshooting:")
        print("  - Check your app/__init__.py for errors")
        print("  - Ensure all required environment variables are set")
        print("  - Check for database connection issues")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Warehouse Management System - Quick Test")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print("-" * 60)
    
    success = test_app_creation()
    
    print("-" * 60)
    if success:
        print("All tests passed! The application should be ready to run.")
        sys.exit(0)
    else:
        print("Tests failed. Please fix the issues before running the application.")
        sys.exit(1)
