#!/bin/bash
# Build Docker images locally
# Usage: ./scripts/build_docker.sh [tag]

set -e

TAG="${1:-local}"
IMAGE_NAME="kybra-simple-token"

echo "Building Docker images with tag: $TAG"

# Build base image
echo "Building base image..."
docker build -t "$IMAGE_NAME:$TAG" --target base ./token

# Build test image
echo "Building test image..."
docker build -t "$IMAGE_NAME:test-$TAG" --target test ./token

echo ""
echo "✅ Docker images built:"
docker images | grep "$IMAGE_NAME"
