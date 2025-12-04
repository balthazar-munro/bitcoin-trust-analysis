#!/bin/bash

# Streamlit App Demo Runner
# This script launches the Crypto-Trust Analytics Streamlit application

echo "=========================================="
echo "  Crypto-Trust Analytics - Demo Launch"
echo "=========================================="

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    echo "Please run this script from the project directory."
    exit 1
fi

# Check if dataset exists
if [ ! -f "soc-sign-bitcoinotc.csv" ]; then
    echo "⚠️  Warning: Dataset not found!"
    echo "Attempting to extract from .gz file..."
    
    if [ -f "soc-sign-bitcoinotc.csv.gz" ]; then
        gunzip -k soc-sign-bitcoinotc.csv.gz
        echo "✓ Dataset extracted successfully"
    else
        echo "❌ Error: No dataset available"
        echo "Please download soc-sign-bitcoinotc.csv"
        exit 1
    fi
fi

# Check Python packages
echo ""
echo "Checking dependencies..."

python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Streamlit not installed"
    echo "Installing dependencies..."
    pip install -q -r requirements_streamlit.txt
fi

echo "✓ All dependencies ready"
echo ""

# Launch app
echo "=========================================="
echo "  Launching Streamlit App..."
echo "=========================================="
echo ""
echo "The app will open automatically in your browser."
echo "If not, navigate to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
