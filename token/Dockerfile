FROM ghcr.io/smart-social-contracts/icp-dev-env:db60540 AS base

RUN apt-get update && apt-get install -y --no-install-recommends procps nano jq && rm -rf /var/lib/apt/lists/*

# Set default dfx version
RUN dfxvm default 0.29.0

WORKDIR /app

# Dependencies
COPY requirements.txt ./requirements.txt
COPY package.json ./package.json
COPY package-lock.json ./package-lock.json

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Node dependencies
RUN npm ci

# Configuration files
COPY dfx.json ./dfx.json
COPY tsconfig.json ./tsconfig.json

# Source code
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts

# Test stage
FROM base AS test

# Run tests by default
CMD ["python3", "tests/backend/test_token.py"]
