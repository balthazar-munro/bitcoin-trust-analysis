#!/bin/bash

# Crypto-Trust Project Setup Script

echo "========================================"
echo "Crypto-Trust Setup"
echo "========================================"

# Check Python version
echo -e "\n1. Checking Python installation..."
python3 --version

# Create virtual environment
echo -e "\n2. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "\n3. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for dataset
echo -e "\n4. Checking for dataset..."
if [ -f "soc-sign-bitcoinotc.csv" ]; then
    echo "✓ Dataset found: soc-sign-bitcoinotc.csv"
    echo "  File size: $(du -h soc-sign-bitcoinotc.csv | cut -f1)"
else
    echo "⚠ Dataset not found!"
    echo ""
    echo "Please download the Bitcoin OTC dataset:"
    echo "  1. Visit: https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html"
    echo "  2. Download: soc-sign-bitcoinotc.csv.gz"
    echo "  3. Extract to this directory: soc-sign-bitcoinotc.csv"
    echo ""
    echo "Alternative: Use wget (if available)"
    echo "  wget https://snap.stanford.edu/data/soc-sign-bitcoinotc.csv.gz"
    echo "  gunzip soc-sign-bitcoinotc.csv.gz"
fi

echo -e "\n5. Setup complete!"
echo ""
echo "To get started:"
echo "  source venv/bin/activate"
echo "  jupyter notebook crypto_trust_analysis.ipynb"
echo ""
echo "========================================"
