#!/bin/bash

# Test runner script for OpenClaw Claude Config

set -e

echo "🧪 Running OpenClaw Claude Config Tests"
echo "======================================"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed"
    echo "Install it with: pip install pytest pytest-cov"
    exit 1
fi

# Run tests with coverage
echo ""
echo "Running unit tests..."
pytest tests/ -v --tb=short --cov=src --cov-report=html --cov-report=term

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Coverage report: htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
