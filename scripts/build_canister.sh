#!/bin/bash
# Build canister and extract wasm/did artifacts
# Usage: ./scripts/build_canister.sh [output_dir]

set -e

OUTPUT_DIR="${1:-artifacts}"
mkdir -p "$OUTPUT_DIR"

echo "Building token_backend canister..."

cd token

# Start dfx if not running
if ! dfx ping &>/dev/null; then
    echo "Starting dfx..."
    dfx start --background --clean
    sleep 2
fi

# Build the canister
dfx build token_backend

# Copy artifacts
cp .kybra/token_backend/token_backend.wasm "../$OUTPUT_DIR/"
cp src/token_backend/token_backend.did "../$OUTPUT_DIR/"

# Create gzipped version
gzip -k "../$OUTPUT_DIR/token_backend.wasm"

# Build info
echo "Build Date: $(date -u)" > "../$OUTPUT_DIR/BUILD_INFO.txt"
echo "Git SHA: $(git rev-parse HEAD 2>/dev/null || echo 'unknown')" >> "../$OUTPUT_DIR/BUILD_INFO.txt"

echo "✅ Artifacts built successfully:"
ls -la "../$OUTPUT_DIR/"
