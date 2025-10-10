#!/bin/bash

# DOCX to PDF Converter - Setup Script

echo "🚀 Setting up DOCX to PDF Converter..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if LibreOffice is installed
if ! command -v libreoffice &> /dev/null; then
    echo "⚠️  LibreOffice not found. Please install LibreOffice:"
    echo "   macOS: brew install --cask libreoffice"
    echo "   Ubuntu: sudo apt install libreoffice"
    echo "   Windows: Download from https://www.libreoffice.org/"
    echo ""
    echo "Continuing with setup anyway..."
else
    echo "✅ LibreOffice found: $(libreoffice --version)"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p temp
mkdir -p output
mkdir -p logs

# Make test script executable
chmod +x test_converter.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To run tests:"
echo "  python test_converter.py"
echo ""
echo "Server will be available at: http://localhost:8080"
