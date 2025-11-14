#!/bin/bash

# Quick Start Script for Air Algerie Flight Price Scraper

echo "========================================="
echo "Air Algerie Flight Price Scraper Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)

if [ $? -eq 0 ]; then
    echo "✓ Python found: $python_version"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Chrome/Chromium
echo ""
echo "Checking Chrome/Chromium..."
if command -v google-chrome &> /dev/null; then
    chrome_version=$(google-chrome --version)
    echo "✓ Chrome found: $chrome_version"
elif command -v chromium &> /dev/null; then
    chrome_version=$(chromium --version)
    echo "✓ Chromium found: $chrome_version"
else
    echo "⚠ Chrome/Chromium not found. Selenium may not work properly."
    echo "  Install Chrome: https://www.google.com/chrome/"
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Error installing dependencies"
    exit 1
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x airalgerie_scraper.py
chmod +x airalgerie_parser.py
chmod +x batch_scraper.py
chmod +x analyze_prices.py

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Quick Start Commands:"
echo ""
echo "1. Parse existing URLs:"
echo "   python3 airalgerie_parser.py"
echo ""
echo "2. Batch scrape from URL file:"
echo "   python3 batch_scraper.py example_urls.txt"
echo ""
echo "3. Full automated search (requires configuration):"
echo "   python3 airalgerie_scraper.py"
echo ""
echo "4. Analyze results:"
echo "   python3 analyze_prices.py --report"
echo ""
echo "See README.md for detailed instructions."
echo ""
