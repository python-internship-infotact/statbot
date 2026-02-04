#!/usr/bin/env python3
"""
Production startup script for StatBot Pro
Handles environment setup and graceful startup
"""

import os
import sys
import logging
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = ['workspace', 'static', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory '{directory}' ready")

def setup_logging():
    """Configure logging for production"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/statbot.log')
        ]
    )

def check_environment():
    """Check required environment variables"""
    required_vars = []
    optional_vars = {
        'PORT': '8001',
        'HOST': '0.0.0.0',
        'ENVIRONMENT': 'production',
        'CORS_ORIGINS': 'http://localhost:3000'
    }
    
    # Set default values for optional variables
    for var, default in optional_vars.items():
        if var not in os.environ:
            os.environ[var] = default
            print(f"✓ Set {var}={default} (default)")
        else:
            print(f"✓ {var}={os.environ[var]}")
    
    # Check required variables
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🚀 Starting StatBot Pro...")
    
    # Setup
    setup_directories()
    setup_logging()
    check_environment()
    
    print("✓ Environment setup complete")
    print(f"✓ Starting server on {os.environ['HOST']}:{os.environ['PORT']}")
    
    # Import and run the main application
    try:
        from main import app
        import uvicorn
        
        uvicorn.run(
            "main:app",
            host=os.environ['HOST'],
            port=int(os.environ['PORT']),
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()