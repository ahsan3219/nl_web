#!/bin/bash

# Render deployment startup script
echo "Starting Zenti AI Agent on Render..."

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
    echo "No PORT environment variable found, using default: $PORT"
else
    echo "Using PORT from environment: $PORT"
fi

# Change to the correct directory
cd code/python

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "Starting server on port $PORT..."
python app-file.py
