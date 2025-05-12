#!/bin/bash
echo "Setting up QUT Course Scraper environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data

echo "Environment setup complete."
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the scraper, run: python main.py"
