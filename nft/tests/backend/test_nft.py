#!/usr/bin/env python3
"""
Tests for the ICRC-7/ICRC-37 NFT backend.
Tests basic NFT operations using mock storage.
"""

import os
import sys
import time
import json
from types import ModuleType
from unittest.mock import MagicMock


# Create subscriptable mock types
class SubscriptableMeta(type):
    def __getitem__(cls, item):
        return cls


class MockOpt(metaclass=SubscriptableMeta):
    pass


class MockVec(metaclass=SubscriptableMeta):
    pass


class MockTuple(metaclass=SubscriptableMeta):
    pass


class MockAlias(metaclass=SubscriptableMeta):
    pass


class MockAsync(metaclass=SubscriptableMeta):
    pass


class MockCallResult(metaclass=SubscriptableMeta):
    pass


class MockStableBTreeMap(metaclass=SubscriptableMeta):
    def __init__(self, memory_id=0, max_key_size=100, max_value_size=100):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def insert(self, key, value):
        self.data[key] = value

    def items(self):
        return self.data.items()


class MockRecord:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._data = kwargs

    def __getitem__(self, key):
        return self._data.get(key)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __call__(self, **kwargs):
        return MockRecord(**kwargs)


class MockVariant:
    """Mock Variant class for testing"""

    def __init__(self, mapping=None, **kwargs):
        if mapping:
            self._mapping = mapping
        for k, v in kwargs.items():
            setattr(self, k, v)
            self._data = {k: v}

    def __init_subclass__(cls, **kwargs):
        pass

    def __call__(self, **kwargs):
        return MockVariant(**kwargs)

    def __contains__(self, item):
        return hasattr(self, '_data') and item in self._data


class MockPrincipal:
    def __init__(self, principal_str="aaaaa-aa"):
        self._str = principal_str

    def to_str(self):
        return self._str

    @classmethod
    def from_str(cls, s):
        return cls(s)


# Create mock modules BEFORE any imports
mock_kybra = ModuleType("kybra")
mock_ic = MagicMock()
mock_ic.time.return_value = int(time.time() * 1_000_000_000)
mock_ic.caller.return_value = MockPrincipal("aaaaa-aa")
mock_ic.id.return_value = MockPrincipal("bbbbb-bb")

mock_kybra.ic = mock_ic
mock_kybra.Alias = MockAlias
mock_kybra.Async = MockAsync
mock_kybra.CallResult = MockCallResult
mock_kybra.Opt = MockOpt
mock_kybra.Principal = MockPrincipal
mock_kybra.Record = MockRecord
mock_kybra.StableBTreeMap = MockStableBTreeMap
mock_kybra.Tuple = MockTuple
mock_kybra.Variant = MockVariant
mock_kybra.Vec = MockVec
mock_kybra.blob = bytes
mock_kybra.init = lambda f: f
mock_kybra.nat = int
mock_kybra.nat8 = int
mock_kybra.nat32 = int
mock_kybra.nat64 = int
mock_kybra.query = lambda f: f
mock_kybra.text = str
mock_kybra.update = lambda f: f
mock_kybra.void = type(None)

sys.modules["kybra"] = mock_kybra

# Mock kybra_simple_logging
mock_logging = ModuleType("kybra_simple_logging")
mock_logger = MagicMock()
mock_logging.get_logger = lambda name: mock_logger
sys.modules["kybra_simple_logging"] = mock_logging


# Mock kybra_simple_db
class MockStorage:
    """Mock storage for testing without requiring a real canister environment"""

    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def insert(self, key, value):
        self.data[key] = value

    def remove(self, key):
        if key in self.data:
            del self.data[key]

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()


mock_storage = MockStorage()


class MockEntityMeta(type):
    """Metaclass that gives each Entity subclass its own _instances dict"""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._instances = {}
        return cls

    def __getitem__(cls, key):
        return cls._instances.get(key)


class MockEntity(metaclass=MockEntityMeta):
    """Mock Entity class for testing"""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        key = self._get_key(kwargs)
        if key is not None:
            self.__class__._instances[key] = self

    @staticmethod
    def _get_key(data):
        """Get key from dict, handling falsy values like 0 correctly"""
        if "id" in data:
            return data["id"]
        if "key" in data:
            return data["key"]
        return None

    def _get_instance_key(self):
        """Get key from instance attributes"""
        if hasattr(self, "id") and self.id is not None:
            return self.id
        if hasattr(self, "key") and self.key is not None:
            return self.key
        return None

    def save(self):
        key = self._get_instance_key()
        if key is not None:
            self.__class__._instances[key] = self

    def delete(self):
        key = self._get_instance_key()
        if key is not None and key in self.__class__._instances:
            del self.__class__._instances[key]

    @classmethod
    def instances(cls):
        return list(cls._instances.values())

    @classmethod
    def find_all(cls):
        return list(cls._instances.values())

    @classmethod
    def find_by(cls, field, value):
        results = []
        for instance in cls._instances.values():
            if hasattr(instance, field) and getattr(instance, field) == value:
                results.append(instance)
        return results

    @classmethod
    def count(cls):
        return len(cls._instances)


class MockDatabase:
    _instance = None

    @classmethod
    def init(cls, db_storage=None, audit_enabled=False):
        cls._instance = cls()

    @classmethod
    def get_instance(cls):
        return cls._instance

    def register_entity_type(self, entity_class):
        pass


class MockString:
    """Mock String field that accepts kybra-simple-db kwargs"""
    def __new__(cls, max_length=None, default=None, min_length=None):
        return default if default is not None else ""


class MockInteger:
    """Mock Integer field that accepts kybra-simple-db kwargs"""
    def __new__(cls, default=None):
        return default if default is not None else 0


mock_db = ModuleType("kybra_simple_db")
mock_db.Database = MockDatabase
mock_db.Entity = MockEntity
mock_db.Integer = MockInteger
mock_db.String = MockString
sys.modules["kybra_simple_db"] = mock_db

# Add paths to match Kybra's import resolution
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "../../src/nft_backend/src")
)

# Color formatting for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")


def print_failure(message, error=None):
    print(f"{RED}✗ {message}{RESET}")
    if error:
        print(f"  Error: {error}")


# =============================================================================
# Helper to reset state between tests
# =============================================================================

def reset_state():
    """Reset all entity instances for clean test state"""
    from main import NFTToken, NFTCollection, NFTApproval, NFTTransactionLog
    NFTToken._instances.clear()
    NFTCollection._instances.clear()
    NFTApproval._instances.clear()
    NFTTransactionLog._instances.clear()


def setup_collection(name="Test NFT", symbol="TNFT", test_mode=True):
    """Set up a test collection"""
    from main import NFTCollection
    collection = NFTCollection(
        id="config",
        name=name,
        symbol=symbol,
        description="Test NFT Collection",
        supply_cap=0,
        total_supply=0,
        tx_count=0,
        test_mode=1 if test_mode else 0
    )
    collection.save()
    return collection


# =============================================================================
# ICRC-7 QUERY METHOD TESTS
# =============================================================================

def test_icrc7_name():
    """Test icrc7_name query"""
    try:
        reset_state()
        setup_collection(name="My NFT Collection")
        
        from main import icrc7_name
        name = icrc7_name()
        assert name == "My NFT Collection", f"Expected 'My NFT Collection', got {name}"
        
        print_success("icrc7_name tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_name tests failed", str(e))
        return False


def test_icrc7_symbol():
    """Test icrc7_symbol query"""
    try:
        reset_state()
        setup_collection(symbol="MYNFT")
        
        from main import icrc7_symbol
        symbol = icrc7_symbol()
        assert symbol == "MYNFT", f"Expected 'MYNFT', got {symbol}"
        
        print_success("icrc7_symbol tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_symbol tests failed", str(e))
        return False


def test_icrc7_total_supply():
    """Test icrc7_total_supply query"""
    try:
        reset_state()
        collection = setup_collection()
        collection.total_supply = 5
        collection.save()
        
        from main import icrc7_total_supply
        supply = icrc7_total_supply()
        assert supply == 5, f"Expected 5, got {supply}"
        
        print_success("icrc7_total_supply tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_total_supply tests failed", str(e))
        return False


def test_icrc7_supply_cap():
    """Test icrc7_supply_cap query"""
    try:
        reset_state()
        
        # Test no cap (returns None)
        collection = setup_collection()
        collection.supply_cap = 0
        collection.save()
        
        from main import icrc7_supply_cap
        cap = icrc7_supply_cap()
        assert cap is None, f"Expected None for no cap, got {cap}"
        
        # Test with cap
        collection.supply_cap = 100
        collection.save()
        cap = icrc7_supply_cap()
        assert cap == 100, f"Expected 100, got {cap}"
        
        print_success("icrc7_supply_cap tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_supply_cap tests failed", str(e))
        return False


def test_icrc7_owner_of():
    """Test icrc7_owner_of query"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc7_owner_of
        
        # Create a token
        token = NFTToken(
            id=1,
            owner_principal="alice-principal",
            owner_subaccount="",
            metadata_json="{}"
        )
        token.save()
        
        # Query owner
        owner = icrc7_owner_of(1)
        assert owner is not None, "Owner should not be None"
        assert owner["owner"].to_str() == "alice-principal", f"Expected alice-principal, got {owner['owner'].to_str()}"
        
        # Query non-existent token
        owner2 = icrc7_owner_of(999)
        assert owner2 is None, "Owner of non-existent token should be None"
        
        print_success("icrc7_owner_of tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_owner_of tests failed", str(e))
        return False


def test_icrc7_balance_of():
    """Test icrc7_balance_of query"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc7_balance_of, Account
        
        # Create tokens for alice
        for i in range(3):
            token = NFTToken(
                id=i,
                owner_principal="alice-principal",
                owner_subaccount="",
                metadata_json="{}"
            )
            token.save()
        
        # Create token for bob
        token = NFTToken(
            id=10,
            owner_principal="bob-principal",
            owner_subaccount="",
            metadata_json="{}"
        )
        token.save()
        
        # Check alice's balance
        alice_account = {"owner": MockPrincipal("alice-principal"), "subaccount": None}
        balance = icrc7_balance_of(alice_account)
        assert balance == 3, f"Expected 3 for alice, got {balance}"
        
        # Check bob's balance
        bob_account = {"owner": MockPrincipal("bob-principal"), "subaccount": None}
        balance = icrc7_balance_of(bob_account)
        assert balance == 1, f"Expected 1 for bob, got {balance}"
        
        # Check charlie's balance (no tokens)
        charlie_account = {"owner": MockPrincipal("charlie-principal"), "subaccount": None}
        balance = icrc7_balance_of(charlie_account)
        assert balance == 0, f"Expected 0 for charlie, got {balance}"
        
        print_success("icrc7_balance_of tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_balance_of tests failed", str(e))
        return False


def test_icrc7_tokens():
    """Test icrc7_tokens query"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc7_tokens
        
        # Create tokens with various IDs
        for token_id in [5, 2, 8, 1, 10]:
            token = NFTToken(
                id=token_id,
                owner_principal="owner",
                owner_subaccount="",
                metadata_json="{}"
            )
            token.save()
        
        # Get all tokens (should be sorted)
        tokens = icrc7_tokens(None, None)
        assert tokens == [1, 2, 5, 8, 10], f"Expected sorted tokens, got {tokens}"
        
        # Test pagination with prev
        tokens = icrc7_tokens(2, None)
        assert tokens == [5, 8, 10], f"Expected [5, 8, 10], got {tokens}"
        
        # Test pagination with take
        tokens = icrc7_tokens(None, 3)
        assert tokens == [1, 2, 5], f"Expected [1, 2, 5], got {tokens}"
        
        print_success("icrc7_tokens tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_tokens tests failed", str(e))
        return False


def test_icrc7_tokens_of():
    """Test icrc7_tokens_of query"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc7_tokens_of
        
        # Create tokens for alice
        for token_id in [3, 1, 7]:
            token = NFTToken(
                id=token_id,
                owner_principal="alice",
                owner_subaccount="",
                metadata_json="{}"
            )
            token.save()
        
        # Create tokens for bob
        for token_id in [2, 5]:
            token = NFTToken(
                id=token_id,
                owner_principal="bob",
                owner_subaccount="",
                metadata_json="{}"
            )
            token.save()
        
        alice_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        bob_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        
        # Get alice's tokens
        tokens = icrc7_tokens_of(alice_account, None, None)
        assert tokens == [1, 3, 7], f"Expected [1, 3, 7], got {tokens}"
        
        # Get bob's tokens
        tokens = icrc7_tokens_of(bob_account, None, None)
        assert tokens == [2, 5], f"Expected [2, 5], got {tokens}"
        
        print_success("icrc7_tokens_of tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_tokens_of tests failed", str(e))
        return False


# =============================================================================
# MINT TESTS
# =============================================================================

def test_mint_success():
    """Test successful NFT minting"""
    try:
        reset_state()
        setup_collection(test_mode=True)
        
        from main import mint, NFTToken, NFTCollection
        
        # Mint an NFT
        owner_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        result = mint({
            "token_id": 1,
            "owner": owner_account,
            "metadata": [("name", {"Text": "My First NFT"})]
        })
        
        assert "Ok" in result, f"Expected Ok result, got {result}"
        
        # Verify token was created
        token = NFTToken[1]
        assert token is not None, "Token should exist"
        assert token.owner_principal == "alice", f"Expected alice, got {token.owner_principal}"
        
        # Verify supply increased
        collection = NFTCollection["config"]
        assert collection.total_supply == 1, f"Expected total_supply=1, got {collection.total_supply}"
        
        print_success("mint_success tests passed")
        return True
    except Exception as e:
        print_failure("mint_success tests failed", str(e))
        return False


def test_mint_duplicate_token_id():
    """Test minting with duplicate token ID fails"""
    try:
        reset_state()
        setup_collection(test_mode=True)
        
        from main import mint, NFTToken
        
        # Create existing token
        token = NFTToken(id=1, owner_principal="bob", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Try to mint with same ID
        owner_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        result = mint({
            "token_id": 1,
            "owner": owner_account,
            "metadata": None
        })
        
        assert "Err" in result, f"Expected Err result, got {result}"
        
        print_success("mint_duplicate_token_id tests passed")
        return True
    except Exception as e:
        print_failure("mint_duplicate_token_id tests failed", str(e))
        return False


def test_mint_supply_cap_reached():
    """Test minting fails when supply cap is reached"""
    try:
        reset_state()
        collection = setup_collection(test_mode=True)
        collection.supply_cap = 2
        collection.total_supply = 2
        collection.save()
        
        from main import mint
        
        owner_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        result = mint({
            "token_id": 100,
            "owner": owner_account,
            "metadata": None
        })
        
        assert "Err" in result, f"Expected Err result, got {result}"
        
        print_success("mint_supply_cap_reached tests passed")
        return True
    except Exception as e:
        print_failure("mint_supply_cap_reached tests failed", str(e))
        return False


# =============================================================================
# ICRC-7 TRANSFER TESTS
# =============================================================================

def test_icrc7_transfer_success():
    """Test successful NFT transfer"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc7_transfer, NFTTransactionLog
        
        # Create token owned by caller (aaaaa-aa)
        token = NFTToken(id=1, owner_principal="aaaaa-aa", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Transfer to bob
        to_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        results = icrc7_transfer([{
            "from_subaccount": None,
            "to": to_account,
            "token_id": 1,
            "memo": None,
            "created_at_time": None
        }])
        
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert "Ok" in results[0], f"Expected Ok result, got {results[0]}"
        
        # Verify ownership changed
        token = NFTToken[1]
        assert token.owner_principal == "bob", f"Expected bob, got {token.owner_principal}"
        
        # Verify transaction was logged
        assert NFTTransactionLog.count() == 1, "Transaction should be logged"
        
        print_success("icrc7_transfer_success tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_transfer_success tests failed", str(e))
        return False


def test_icrc7_transfer_not_owner():
    """Test transfer fails when caller is not owner"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc7_transfer
        
        # Create token owned by alice (not caller)
        token = NFTToken(id=1, owner_principal="alice", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Try to transfer (caller is aaaaa-aa, not alice)
        to_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        results = icrc7_transfer([{
            "from_subaccount": None,
            "to": to_account,
            "token_id": 1,
            "memo": None,
            "created_at_time": None
        }])
        
        assert "Err" in results[0], f"Expected Err result, got {results[0]}"
        
        # Verify ownership did NOT change
        token = NFTToken[1]
        assert token.owner_principal == "alice", f"Owner should still be alice"
        
        print_success("icrc7_transfer_not_owner tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_transfer_not_owner tests failed", str(e))
        return False


def test_icrc7_transfer_non_existent():
    """Test transfer fails for non-existent token"""
    try:
        reset_state()
        setup_collection()
        
        from main import icrc7_transfer
        
        to_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        results = icrc7_transfer([{
            "from_subaccount": None,
            "to": to_account,
            "token_id": 999,
            "memo": None,
            "created_at_time": None
        }])
        
        assert "Err" in results[0], f"Expected Err result, got {results[0]}"
        
        print_success("icrc7_transfer_non_existent tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_transfer_non_existent tests failed", str(e))
        return False


# =============================================================================
# ICRC-37 APPROVAL TESTS
# =============================================================================

def test_icrc37_approve_tokens():
    """Test approving a spender for specific tokens"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc37_approve_tokens, NFTApproval
        
        # Create token owned by caller
        token = NFTToken(id=1, owner_principal="aaaaa-aa", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Approve bob as spender
        spender_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        results = icrc37_approve_tokens([{
            "token_id": 1,
            "approval_info": {
                "spender": spender_account,
                "from_subaccount": None,
                "expires_at": None,
                "memo": None,
                "created_at_time": None
            }
        }])
        
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert "Ok" in results[0], f"Expected Ok result, got {results[0]}"
        
        # Verify approval was created
        assert NFTApproval.count() == 1, "Approval should exist"
        
        print_success("icrc37_approve_tokens tests passed")
        return True
    except Exception as e:
        print_failure("icrc37_approve_tokens tests failed", str(e))
        return False


def test_icrc37_approve_not_owner():
    """Test approval fails when caller is not owner"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc37_approve_tokens
        
        # Create token owned by alice (not caller)
        token = NFTToken(id=1, owner_principal="alice", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Try to approve (caller is aaaaa-aa, not alice)
        spender_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        results = icrc37_approve_tokens([{
            "token_id": 1,
            "approval_info": {
                "spender": spender_account,
                "from_subaccount": None,
                "expires_at": None,
                "memo": None,
                "created_at_time": None
            }
        }])
        
        assert "Err" in results[0], f"Expected Err result, got {results[0]}"
        
        print_success("icrc37_approve_not_owner tests passed")
        return True
    except Exception as e:
        print_failure("icrc37_approve_not_owner tests failed", str(e))
        return False


def test_icrc37_is_approved():
    """Test checking if spender is approved"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, NFTApproval, icrc37_is_approved
        
        # Create token
        token = NFTToken(id=1, owner_principal="alice", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Create approval for bob
        approval = NFTApproval(
            id="token:1:alice:bob",
            approval_type="token",
            token_id=1,
            owner_principal="alice",
            owner_subaccount="",
            spender_principal="bob",
            spender_subaccount="",
            expires_at=0,
            created_at=0
        )
        approval.save()
        
        # Check bob is approved
        bob_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        is_approved = icrc37_is_approved(bob_account, None, 1)
        assert is_approved == True, "Bob should be approved"
        
        # Check charlie is NOT approved
        charlie_account = {"owner": MockPrincipal("charlie"), "subaccount": None}
        is_approved = icrc37_is_approved(charlie_account, None, 1)
        assert is_approved == False, "Charlie should not be approved"
        
        print_success("icrc37_is_approved tests passed")
        return True
    except Exception as e:
        print_failure("icrc37_is_approved tests failed", str(e))
        return False


def test_icrc37_transfer_from_success():
    """Test transfer_from with approval"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, NFTApproval, icrc37_transfer_from
        
        # Create token owned by alice
        token = NFTToken(id=1, owner_principal="alice", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Create approval for caller (aaaaa-aa)
        approval = NFTApproval(
            id="token:1:alice:aaaaa-aa",
            approval_type="token",
            token_id=1,
            owner_principal="alice",
            owner_subaccount="",
            spender_principal="aaaaa-aa",
            spender_subaccount="",
            expires_at=0,
            created_at=0
        )
        approval.save()
        
        # Transfer from alice to charlie (as approved spender)
        from_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        to_account = {"owner": MockPrincipal("charlie"), "subaccount": None}
        
        results = icrc37_transfer_from([{
            "spender_subaccount": None,
            "from_": from_account,
            "to": to_account,
            "token_id": 1,
            "memo": None,
            "created_at_time": None
        }])
        
        assert "Ok" in results[0], f"Expected Ok result, got {results[0]}"
        
        # Verify ownership changed
        token = NFTToken[1]
        assert token.owner_principal == "charlie", f"Expected charlie, got {token.owner_principal}"
        
        print_success("icrc37_transfer_from_success tests passed")
        return True
    except Exception as e:
        print_failure("icrc37_transfer_from_success tests failed", str(e))
        return False


def test_icrc37_transfer_from_no_approval():
    """Test transfer_from fails without approval"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, icrc37_transfer_from
        
        # Create token owned by alice
        token = NFTToken(id=1, owner_principal="alice", owner_subaccount="", metadata_json="{}")
        token.save()
        
        # Try transfer without approval
        from_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        to_account = {"owner": MockPrincipal("charlie"), "subaccount": None}
        
        results = icrc37_transfer_from([{
            "spender_subaccount": None,
            "from_": from_account,
            "to": to_account,
            "token_id": 1,
            "memo": None,
            "created_at_time": None
        }])
        
        assert "Err" in results[0], f"Expected Err result, got {results[0]}"
        
        # Verify ownership did NOT change
        token = NFTToken[1]
        assert token.owner_principal == "alice", f"Owner should still be alice"
        
        print_success("icrc37_transfer_from_no_approval tests passed")
        return True
    except Exception as e:
        print_failure("icrc37_transfer_from_no_approval tests failed", str(e))
        return False


def test_icrc37_collection_approval():
    """Test collection-level approvals"""
    try:
        reset_state()
        setup_collection()
        
        from main import NFTToken, NFTApproval, icrc37_transfer_from
        
        # Create multiple tokens owned by alice
        for i in [1, 2, 3]:
            token = NFTToken(id=i, owner_principal="alice", owner_subaccount="", metadata_json="{}")
            token.save()
        
        # Create COLLECTION-level approval for caller
        approval = NFTApproval(
            id="collection:alice:aaaaa-aa",
            approval_type="collection",
            token_id=0,
            owner_principal="alice",
            owner_subaccount="",
            spender_principal="aaaaa-aa",
            spender_subaccount="",
            expires_at=0,
            created_at=0
        )
        approval.save()
        
        # Transfer token 2 using collection approval
        from_account = {"owner": MockPrincipal("alice"), "subaccount": None}
        to_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        
        results = icrc37_transfer_from([{
            "spender_subaccount": None,
            "from_": from_account,
            "to": to_account,
            "token_id": 2,
            "memo": None,
            "created_at_time": None
        }])
        
        assert "Ok" in results[0], f"Expected Ok result, got {results[0]}"
        
        # Verify token 2 transferred
        token = NFTToken[2]
        assert token.owner_principal == "bob", f"Expected bob, got {token.owner_principal}"
        
        # Tokens 1 and 3 should still be owned by alice
        assert NFTToken[1].owner_principal == "alice"
        assert NFTToken[3].owner_principal == "alice"
        
        print_success("icrc37_collection_approval tests passed")
        return True
    except Exception as e:
        print_failure("icrc37_collection_approval tests failed", str(e))
        return False


# =============================================================================
# TRANSACTION LOG TESTS
# =============================================================================

def test_transaction_logging():
    """Test transaction logging for various operations"""
    try:
        reset_state()
        setup_collection(test_mode=True)
        
        from main import mint, icrc7_transfer, NFTTransactionLog
        
        # Mint
        owner_account = {"owner": MockPrincipal("aaaaa-aa"), "subaccount": None}
        mint({"token_id": 1, "owner": owner_account, "metadata": None})
        
        # Transfer
        to_account = {"owner": MockPrincipal("bob"), "subaccount": None}
        icrc7_transfer([{
            "from_subaccount": None,
            "to": to_account,
            "token_id": 1,
            "memo": None,
            "created_at_time": None
        }])
        
        # Verify transaction log
        txs = NFTTransactionLog.find_all()
        assert len(txs) == 2, f"Expected 2 transactions, got {len(txs)}"
        
        # Check mint transaction
        mint_tx = [t for t in txs if t.kind == "mint"][0]
        assert mint_tx.to_principal == "aaaaa-aa"
        
        # Check transfer transaction
        transfer_tx = [t for t in txs if t.kind == "transfer"][0]
        assert transfer_tx.from_principal == "aaaaa-aa"
        assert transfer_tx.to_principal == "bob"
        
        print_success("transaction_logging tests passed")
        return True
    except Exception as e:
        print_failure("transaction_logging tests failed", str(e))
        return False


def test_get_transactions():
    """Test get_transactions query"""
    try:
        reset_state()
        setup_collection(test_mode=True)
        
        from main import mint, get_transactions
        
        # Create several transactions
        for i in range(5):
            owner_account = {"owner": MockPrincipal(f"user{i}"), "subaccount": None}
            mint({"token_id": i, "owner": owner_account, "metadata": None})
        
        # Get all transactions
        txs = get_transactions(0, 10)
        assert len(txs) == 5, f"Expected 5 transactions, got {len(txs)}"
        
        # Get subset
        txs = get_transactions(1, 2)
        assert len(txs) == 2, f"Expected 2 transactions, got {len(txs)}"
        
        print_success("get_transactions tests passed")
        return True
    except Exception as e:
        print_failure("get_transactions tests failed", str(e))
        return False


# =============================================================================
# SUPPORTED STANDARDS TEST
# =============================================================================

def test_icrc7_supported_standards():
    """Test icrc7_supported_standards query"""
    try:
        reset_state()
        setup_collection()
        
        from main import icrc7_supported_standards
        
        standards = icrc7_supported_standards()
        assert len(standards) >= 2, f"Expected at least 2 standards, got {len(standards)}"
        
        # Check both standards are listed
        standard_names = [s.get("name", s["name"]) if isinstance(s, dict) else s.name for s in standards]
        assert "ICRC-7" in standard_names, "ICRC-7 should be in supported standards"
        assert "ICRC-37" in standard_names, "ICRC-37 should be in supported standards"
        
        print_success("icrc7_supported_standards tests passed")
        return True
    except Exception as e:
        print_failure("icrc7_supported_standards tests failed", str(e))
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_tests():
    """Run all tests and report results"""
    print(f"{BOLD}Running NFT Backend Tests (ICRC-7/ICRC-37)...{RESET}\n")

    success_count = 0
    failure_count = 0

    tests = [
        # ICRC-7 Query tests
        test_icrc7_name,
        test_icrc7_symbol,
        test_icrc7_total_supply,
        test_icrc7_supply_cap,
        test_icrc7_owner_of,
        test_icrc7_balance_of,
        test_icrc7_tokens,
        test_icrc7_tokens_of,
        test_icrc7_supported_standards,
        # Mint tests
        test_mint_success,
        test_mint_duplicate_token_id,
        test_mint_supply_cap_reached,
        # ICRC-7 Transfer tests
        test_icrc7_transfer_success,
        test_icrc7_transfer_not_owner,
        test_icrc7_transfer_non_existent,
        # ICRC-37 Approval tests
        test_icrc37_approve_tokens,
        test_icrc37_approve_not_owner,
        test_icrc37_is_approved,
        test_icrc37_transfer_from_success,
        test_icrc37_transfer_from_no_approval,
        test_icrc37_collection_approval,
        # Transaction log tests
        test_transaction_logging,
        test_get_transactions,
    ]

    for test in tests:
        if test():
            success_count += 1
        else:
            failure_count += 1

    print(f"\n{BOLD}Test Summary:{RESET}")
    print(f"- {GREEN}{success_count} tests passed{RESET}")
    print(f"- {RED if failure_count > 0 else ''}{failure_count} tests failed{RESET}")

    return failure_count == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
