#!/bin/bash
# Setup script for the Airline Booking App

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install specific packages if they're missing
pip install flask requests beautifulsoup4

# Run the application
python app.py