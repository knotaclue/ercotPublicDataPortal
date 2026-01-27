#!/bin/bash
#
# ERCOT API Query Tool - Setup Script
# 
# This script helps you set up the project quickly by:
# 1. Creating a virtual environment (optional)
# 2. Installing dependencies
# 3. Creating .env file from template
# 4. Verifying the setup
#
# Usage: ./setup.sh

set -e  # Exit on any error

echo "=========================================="
echo "ERCOT API Query Tool - Setup"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Python 3 is installed
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi
echo ""

# Ask if user wants to create a virtual environment
echo "Do you want to create a virtual environment? (recommended)"
read -p "Create virtual environment? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
    else
        echo "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
    echo ""
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet
print_success "Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ -f ".env" ]; then
    print_warning ".env file already exists. Skipping creation."
    echo "If you need to recreate it, run: cp .env.template .env"
else
    echo "Creating .env file from template..."
    cp .env.template .env
    print_success ".env file created"
    echo ""
    print_warning "IMPORTANT: Edit .env file and add your ERCOT credentials:"
    echo "  - ERCOT_USERNAME"
    echo "  - ERCOT_PASSWORD"
    echo "  - ERCOT_SUBSCRIPTION_KEY"
    echo ""
    read -p "Would you like to edit .env now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
fi
echo ""

# Create output directory
if [ ! -d "output" ]; then
    mkdir -p output
    print_success "Output directory created"
else
    print_warning "Output directory already exists"
fi
echo ""

# Verify setup
echo "Verifying setup..."
echo ""

# Check if .env has been configured
if grep -q "your_username_here" .env 2>/dev/null; then
    print_warning ".env file still contains placeholder values"
    echo "  Please edit .env and add your actual credentials before running queries"
else
    print_success ".env file appears to be configured"
fi

# Check if query examples exist
if [ -f "queries/realtime_system_load.json" ]; then
    print_success "Example query configurations found"
else
    print_warning "Example query configurations not found"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
if [ -d "venv" ]; then
    echo "Virtual environment: Created and activated"
    echo "To activate later, run: source venv/bin/activate"
else
    echo "Virtual environment: Not created"
fi
echo "Dependencies: Installed"
echo ".env file: Created (${YELLOW}needs configuration${NC})"
echo "Output directory: Ready"
echo ""

echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Edit your .env file with actual credentials:"
echo "   nano .env"
echo ""
echo "2. Try running an example query:"
echo "   python3 ercot_query.py --config queries/realtime_system_load.json"
echo ""
echo "3. Create your own queries by copying examples:"
echo "   cp queries/realtime_system_load.json queries/my_query.json"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md for a quick guide"
echo "  - README.md for full documentation"
echo "  - EXAMPLES.md for usage examples"
echo ""
print_success "Setup complete!"
echo ""
