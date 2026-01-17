#!/bin/bash
# Deploy canisters to staging network
# Usage: ./token/scripts/deploy_staging.sh
# Requires: DFX identity with cycles

set -e

# Ensure dfxvm default is set (may be reset by volume mounts)
dfxvm default 0.29.0 2>/dev/null || true

# Navigate to token dir if we're at repo root
if [ -d "token/src" ]; then
    cd token
fi

echo "🚀 Deploying to staging network..."

# Check identity
IDENTITY=$(dfx identity whoami)
echo "Using identity: $IDENTITY"

# Verify canister_ids.json exists and has staging entries
if [ ! -f "canister_ids.json" ]; then
    echo "❌ Error: canister_ids.json not found. Canisters must be created manually first."
    exit 1
fi

if ! grep -q '"staging"' canister_ids.json; then
    echo "❌ Error: No staging canister IDs found in canister_ids.json."
    echo "Canisters must be created manually first (canister creation is expensive)."
    exit 1
fi

echo "✓ Found existing staging canister IDs"

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd src/token_frontend && npm install && cd ../..

# Deploy to staging (upgrade only, no creation)
# --no-wallet prevents automatic canister creation
# --yes auto-confirms Candid interface changes for CI
echo "Deploying canisters to staging (upgrade only)..."
dfx deploy --network staging --no-wallet --yes

# Get canister IDs
BACKEND_ID=$(dfx canister id token_backend --network staging)
FRONTEND_ID=$(dfx canister id token_frontend --network staging)

echo ""
echo "✅ Deployment to staging successful!"
echo ""
echo "Backend canister:  $BACKEND_ID"
echo "Frontend canister: $FRONTEND_ID"
echo ""
echo "Frontend URL: https://${FRONTEND_ID}.icp0.io/"
echo ""

# Verify deployment
echo "Verifying deployment..."
dfx canister call token_backend get_token_info --network staging
dfx canister call token_backend icrc1_name --network staging
