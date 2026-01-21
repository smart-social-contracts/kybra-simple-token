# kybra-simple-token

Token implementations for the Internet Computer using Kybra (Python CDK).

## 🚀 Live Demos

| | Fungible Token (ICRC-1) | NFT (ICRC-7/37) |
|--|-------------------------|-----------------|
| **Try it now** | **[Token App](https://xglmt-7aaaa-aaaah-qq3yq-cai.icp0.io)** | **[NFT App](https://6aqo3-fqaaa-aaaaf-qdohq-cai.icp0.io)** |
| Backend API | [Candid UI](https://a4gq6-oaaaa-aaaab-qaa4q-cai.raw.icp0.io/?id=xbkkh-syaaa-aaaah-qq3ya-cai) | [Candid UI](https://a4gq6-oaaaa-aaaab-qaa4q-cai.raw.icp0.io/?id=6hrip-iiaaa-aaaaf-qdoha-cai) |

---

## Modules

| Module | Standards | Description |
|--------|-----------|-------------|
| [`token/`](./token/) | **ICRC-1** | Fungible token implementation |
| [`nft/`](./nft/) | **ICRC-7, ICRC-37** | NFT with approvals & transfer-from |

---

## ICRC-1 Fungible Token (`token/`)

An ICRC-1 token implementation using `kybra`, `kybra-simple-db`, and `kybra_simple_logging`.

### Canister IDs (Staging)

| Canister | ID | Dashboard |
|----------|----|----|
| Backend | `xbkkh-syaaa-aaaah-qq3ya-cai` | [View](https://dashboard.internetcomputer.org/canister/xbkkh-syaaa-aaaah-qq3ya-cai) |
| Frontend | `xglmt-7aaaa-aaaah-qq3yq-cai` | [View](https://dashboard.internetcomputer.org/canister/xglmt-7aaaa-aaaah-qq3yq-cai) |

### Features

- **ICRC-1 Compliant** - Full ICRC-1 token standard implementation
- **Kybra Python Backend** - Built with Kybra CDK for the Internet Computer
- **SvelteKit Frontend** - Modern web interface with:
  - Token information display
  - Token distribution pie chart visualization
  - Mint tokens UI (when test mode is enabled)
- **Test Mode** - Optional public minting for testing purposes
- **Transaction Indexer** - Built-in transaction history tracking

## Prerequisites

- Python 3.10 or 3.11
- DFX SDK
- Node.js

## Setup

```bash
cd token

# Create and activate virtual environment
python3.10 -m venv ../venv
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install
```

## Deploy Token

```bash
# Start local replica
dfx start --background --clean

# Deploy all canisters
dfx deploy
```

The token is initialized with **1 billion SMPL tokens** (with 8 decimals) assigned to the deployer.

## Query Token Info

```bash
# Get token metadata
dfx canister call token_backend get_token_info

# Get token name
dfx canister call token_backend icrc1_name

# Get token symbol
dfx canister call token_backend icrc1_symbol

# Get total supply
dfx canister call token_backend icrc1_total_supply

# Get your balance
dfx canister call token_backend get_my_balance

# Get your principal
dfx canister call token_backend get_my_principal
```

## Transfer Tokens

Transfer tokens to another principal:

```bash
# Transfer 1000 tokens (with 8 decimals = 100000000000 units)
dfx canister call token_backend icrc1_transfer '(record {
  to = record {
    owner = principal "aaaaa-aa";
    subaccount = null
  };
  amount = 100000000000;
  fee = null;
  memo = null;
  from_subaccount = null;
  created_at_time = null
})'
```

### Transfer Examples

```bash
# Transfer 10 SMPL tokens to a specific principal
dfx canister call token_backend icrc1_transfer '(record {
  to = record {
    owner = principal "rrkah-fqaaa-aaaaa-aaaaq-cai";
    subaccount = null
  };
  amount = 1000000000;
  fee = null;
  memo = null;
  from_subaccount = null;
  created_at_time = null
})'

# Check balance of an account
dfx canister call token_backend icrc1_balance_of '(record {
  owner = principal "rrkah-fqaaa-aaaaa-aaaaq-cai";
  subaccount = null
})'
```

## Mint Tokens

Minting is controlled by the `test` flag during initialization:
- **Test Mode (`test = opt true`)**: Anyone can mint tokens (for testing)
- **Production Mode (`test = opt false` or not set)**: Only the owner can mint

```bash
# Check if test mode is enabled
dfx canister call token_backend is_test_mode

# Get the token owner
dfx canister call token_backend get_owner

# Mint 1000 tokens to a principal
dfx canister call token_backend mint '(record {
  to = record {
    owner = principal "aaaaa-aa";
    subaccount = null
  };
  amount = 100000000000
})'
```

### Mint Examples

```bash
# Mint 500 SMPL to yourself
dfx canister call token_backend mint '(record {
  to = record {
    owner = principal "'$(dfx identity get-principal)'";
    subaccount = null
  };
  amount = 50000000000
})'

# Verify the new total supply
dfx canister call token_backend icrc1_total_supply
```

## Token Distribution

Query the token distribution across all holders:

```bash
# Get all holders and their balances
dfx canister call token_backend get_token_distribution
```

## Token Configuration

| Property | Value |
|----------|-------|
| Name | Simple Token |
| Symbol | SMPL |
| Decimals | 8 |
| Fee | 10,000 (0.0001 SMPL) |
| Initial Supply | 1,000,000,000 SMPL |

## Run Tests

```bash
python3 tests/backend/test_token.py
```

## Project Structure

```
kybra-simple-token/
├── .github/workflows/       # CI/CD workflows
├── token/                   # ICRC-1 Fungible Token
│   ├── src/
│   │   ├── token_backend/   # Kybra Python backend
│   │   └── token_frontend/  # SvelteKit frontend
│   ├── tests/
│   └── dfx.json
├── nft/                     # ICRC-7/ICRC-37 NFT
│   ├── src/
│   │   └── nft_backend/     # Kybra Python backend
│   ├── tests/
│   └── dfx.json
└── README.md
```

---

## ICRC-7/ICRC-37 NFT (`nft/`)

A non-fungible token implementation with approval and transfer-from support.

### Canister IDs (Staging)

| Canister | ID | Dashboard |
|----------|----|----|
| Backend | `6hrip-iiaaa-aaaaf-qdoha-cai` | [View](https://dashboard.internetcomputer.org/canister/6hrip-iiaaa-aaaaf-qdoha-cai) |
| Frontend | `6aqo3-fqaaa-aaaaf-qdohq-cai` | [View](https://dashboard.internetcomputer.org/canister/6aqo3-fqaaa-aaaaf-qdohq-cai) |

### Features

- **ICRC-7** - NFT standard (ownership, metadata, transfers)
- **ICRC-37** - Approval & transfer-from (delegated transfers, marketplace support)
- Transaction history logging
- Supply cap enforcement

### Quick Start

```bash
cd nft
pip install -r requirements.txt
dfx start --clean --background
dfx deploy
```

### Usage

```bash
# Mint an NFT (test mode)
dfx canister call nft_backend mint '(record {
    token_id = 1;
    owner = record { owner = principal "'$(dfx identity get-principal)'"; subaccount = null };
    metadata = opt vec { record { "name"; variant { Text = "My NFT" } } }
})'

# Check owner
dfx canister call nft_backend icrc7_owner_of '(1)'

# Transfer NFT
dfx canister call nft_backend icrc7_transfer '(vec { record {
    from_subaccount = null;
    to = record { owner = principal "xxxxx-xxxxx"; subaccount = null };
    token_id = 1;
    memo = null;
    created_at_time = null
}})'
```

See [`nft/README.md`](./nft/README.md) for full API documentation.

---

## License

MIT
