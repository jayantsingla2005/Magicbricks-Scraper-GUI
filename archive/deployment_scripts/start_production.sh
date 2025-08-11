#!/bin/bash
# MagicBricks Scraper Production Startup Script

echo "Starting MagicBricks Scraper Production System..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Start production system
python production_deployment_system.py

echo "MagicBricks Scraper Production System stopped"
