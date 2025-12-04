#!/bin/bash
# Cross-platform setup script for Browser Agent
# Usage: ./setup.sh

set -e  # Exit on error

echo "🚀 Setting up Browser Agent..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_info "Found Python $PYTHON_VERSION"

# Check if Python version is sufficient
IFS='.' read -ra VERSION_PARTS <<< "$PYTHON_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    # Unix-like systems
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
else
    print_error "Could not find virtual environment activation script"
    exit 1
fi

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_info "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browser
print_info "Installing Playwright browser..."
python -m playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file to add your DeepSeek API key"
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_warning ".env file already exists"
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p logs
mkdir -p chrome_user_data

# Test the setup
print_info "Testing the setup..."
if $PYTHON_CMD -c "import playwright, openai, mcp" &> /dev/null; then
    print_success "All dependencies installed successfully"
else
    print_error "Some dependencies failed to import"
    exit 1
fi

# Create a simple test script
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify the setup.
"""

import sys
from config import config

def main():
    print("Testing Browser Agent setup...")
    
    # Test config loading
    print(f"✓ Config loaded from: {config.PROJECT_ROOT}")
    print(f"✓ Chrome user data: {config.get_chrome_user_data_dir()}")
    print(f"✓ XHS URL: {config.XHS_EXPLORE_URL}")
    
    # Validate config
    if config.validate():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")
        sys.exit(1)
    
    print("\n✅ Setup test passed!")
    print("\nNext steps:")
    print("1. Edit .env file to add your DeepSeek API key")
    print("2. Run: python tests/xhs_search_test.py")
    print("3. Run: python deepseek_agent.py (requires API key)")

if __name__ == "__main__":
    main()
EOF

print_info "Running setup test..."
python test_setup.py

# Clean up test file
rm -f test_setup.py

print_success "🎉 Setup completed successfully!"
echo ""
echo "To get started:"
echo "1. Edit .env file and add your DeepSeek API key"
echo "2. Activate virtual environment:"
echo "   - Unix: source venv/bin/activate"
echo "   - Windows: .\\venv\\Scripts\\Activate.ps1"
echo "3. Run tests: python tests/xhs_search_test.py"
echo ""
echo "For more information, see README.md"