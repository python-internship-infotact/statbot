#!/bin/bash

# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p workspace
mkdir -p static
mkdir -p logs

echo "Setting up permissions..."
chmod 755 workspace
chmod 755 static
chmod 755 logs

echo "Build completed successfully!"