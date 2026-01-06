#!/bin/bash
# Run backend tests locally
# Usage: ./scripts/run_tests.sh

set -e

echo "Running backend tests..."

cd token
python3 tests/backend/test_token.py

echo "✅ All tests passed!"
