#!/bin/bash
# Test runner script for fitting-room-backend

echo "Running tests for fitting-room-backend..."
echo "=========================================="

# Run pytest with coverage
python -m pytest tests/ -v --cov=app --cov=main --cov-report=term-missing

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "✅ All tests passed!"
else
    echo "=========================================="
    echo "❌ Some tests failed."
    exit 1
fi