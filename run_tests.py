#!/usr/bin/env python
"""
Run tests for the Warehouse Management System.
This script provides a simple way to run tests with various options.
"""

import os
import sys
import subprocess
import argparse

sys.path.insert(0, os.path.abspath('.'))

def run_tests(args):
    """Run pytest with the specified arguments."""
    # Base command
    cmd = ["pytest"]
    
    # Add verbosity if requested
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage reporting if requested
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # Run specific tests if specified
    if args.test_file:
        cmd.append(args.test_file)
    
    # Add any additional pytest args
    if args.pytest_args:
        cmd.extend(args.pytest_args)
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode

def setup_environment():
    """Setup the test environment."""
    # Ensure we're using SQLite in memory for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["TESTING"] = "True"
    
    # Use test PLC URL
    os.environ["PLC_OPC_UA_URL"] = "opc.tcp://localhost:4840"
    
    # Disable real backups during tests
    os.environ["BACKUP_INTERVAL"] = "999999"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Warehouse Management System tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage reporting")
    parser.add_argument("-f", "--test-file", help="Run tests in a specific file")
    parser.add_argument("pytest_args", nargs="*", help="Additional pytest arguments")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Run the tests
    sys.exit(run_tests(args))