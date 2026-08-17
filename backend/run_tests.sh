#!/bin/bash

# Test runner script for Financial Advisor backend

echo "================================================"
echo "Financial Advisor Backend - Test Runner"
echo "================================================"
echo ""

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing requirements...${NC}"
    pip install -r requirements.txt
fi

echo -e "${YELLOW}Running tests...${NC}"
echo ""

# Run tests with coverage if available
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short
    TEST_RESULT=$?
    
    echo ""
    if [ $TEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
    else
        echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    fi
    
    exit $TEST_RESULT
else
    echo -e "${RED}❌ Failed to run tests. Please install pytest.${NC}"
    exit 1
fi
