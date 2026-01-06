#!/bin/bash
# Simple script to run all linters from CI workflow locally
# Usage: ./scripts/run_linters.sh [--fix]
#   --fix    Apply fixes automatically when possible (black, isort)

set -e

# Check if we should fix issues or just check
FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
    echo "Running linters in FIX mode..."
else
    echo "Running linters in CHECK mode (use --fix to auto-format)..."
fi

# Target directories
SRC_DIR="token/src/token_backend/src"
TESTS_DIR="token/tests"

# Check/fix formatting with black
echo "Running black..."
if [ "$FIX_MODE" = true ]; then
    black $SRC_DIR $TESTS_DIR
else
    black $SRC_DIR $TESTS_DIR --check
fi

# Check/fix imports with isort
echo "Running isort..."
if [ "$FIX_MODE" = true ]; then
    isort $SRC_DIR $TESTS_DIR
else
    isort $SRC_DIR $TESTS_DIR --check-only
fi

# Lint with flake8
echo "Running flake8..."
flake8 $SRC_DIR --max-line-length=120 --ignore=E501,W503
flake8 $TESTS_DIR --max-line-length=120 --ignore=E501,W503,F401

echo "All linters completed successfully!"
