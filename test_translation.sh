#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting translation test..."

# Function to check if a command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}: $1"
    else
        echo -e "${RED}✗ Failed${NC}: $1"
        exit 1
    fi
}

# Check if python and pip are installed
command -v python3 >/dev/null 2>&1 || { echo "Python3 is required but not installed. Aborting." >&2; exit 1; }
command -v pip >/dev/null 2>&1 || { echo "Pip is required but not installed. Aborting." >&2; exit 1; }

# Install requirements
echo "Installing requirements..."
uv pip install -r requirements.txt
check_status "Installing requirements"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create a .env file with your OPENAI_API_KEY"
    exit 1
fi

# Test English to Chinese translation
echo -e "\nTesting English to Chinese translation..."
uv run mdtranslate.py demo_en.md
check_status "English to Chinese translation and verification"

# Test Chinese to English translation
echo -e "\nTesting Chinese to English translation..."
uv run mdtranslate.py demo_cn.md --to-en
check_status "Chinese to English translation and verification"

echo -e "\n${GREEN}All tests completed successfully!${NC}"
echo "Generated files:"
echo "- demo_en_cn.md (English -> Chinese)"
echo "- demo_cn_en.md (Chinese -> English)" 