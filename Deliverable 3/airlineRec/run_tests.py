#!/usr/bin/env python
"""
Script to run tests for the AirlineRec application
"""
import os
import django
from django.core.management import call_command

def main():
    """Run Django tests for the entire application."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airlineRec.settings')
    django.setup()
    
    # Print header
    print("\n" + "=" * 70)
    print("Running all tests for the AirlineRec application")
    print("=" * 70 + "\n")
    
    # Run the tests - always run all tests in the 'home' app
    call_command('test', 'home', verbosity=2)

if __name__ == '__main__':
    main() 