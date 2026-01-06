#!/usr/bin/env python3
"""
Tests for the ICRC-1 token backend.
Tests basic token operations using mock storage.
"""

import os
import sys
import time
from unittest.mock import MagicMock
from types import ModuleType

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
    pass

# Create mock modules BEFORE any imports
mock_kybra = ModuleType("kybra")
mock_ic = MagicMock()
mock_ic.time.return_value = int(time.time() * 1_000_000_000)
mock_ic.caller.return_value = MagicMock(to_str=lambda: "aaaaa-aa")
mock_ic.id.return_value = MagicMock(to_str=lambda: "bbbbb-bb")

mock_kybra.ic = mock_ic
mock_kybra.Opt = MockOpt
mock_kybra.Principal = MagicMock
mock_kybra.Record = MockRecord
mock_kybra.StableBTreeMap = MockStableBTreeMap
mock_kybra.Tuple = MockTuple
mock_kybra.Vec = MockVec
mock_kybra.blob = bytes
mock_kybra.init = lambda f: f
mock_kybra.nat = int
mock_kybra.nat8 = int
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


class MockEntity:
    """Mock Entity class for testing"""
    _instances = {}
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        key = kwargs.get("id") or kwargs.get("key")
        if key:
            self.__class__._instances[key] = self
    
    def save(self):
        pass
    
    def delete(self):
        key = getattr(self, "id", None) or getattr(self, "key", None)
        if key and key in self.__class__._instances:
            del self.__class__._instances[key]
    
    @classmethod
    def __class_getitem__(cls, key):
        return cls._instances.get(key)
    
    @classmethod
    def instances(cls):
        return cls._instances.values()
    
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


mock_db = ModuleType("kybra_simple_db")
mock_db.Database = MockDatabase
mock_db.Entity = MockEntity
mock_db.Integer = int
mock_db.String = str
sys.modules["kybra_simple_db"] = mock_db

# Add paths to match Kybra's import resolution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/token_backend/src"))

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


def test_token_constants():
    """Test token configuration constants"""
    try:
        # Import after mocking
        from main import TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_FEE
        
        assert TOKEN_NAME == "Simple Token", f"Expected 'Simple Token', got {TOKEN_NAME}"
        assert TOKEN_SYMBOL == "SMPL", f"Expected 'SMPL', got {TOKEN_SYMBOL}"
        assert TOKEN_DECIMALS == 8, f"Expected 8, got {TOKEN_DECIMALS}"
        assert TOKEN_FEE == 10_000, f"Expected 10000, got {TOKEN_FEE}"
        
        print_success("token_constants tests passed")
        return True
    except Exception as e:
        print_failure("token_constants tests failed", str(e))
        return False


def test_icrc1_name():
    """Test icrc1_name query"""
    try:
        from main import icrc1_name
        
        name = icrc1_name()
        assert name == "Simple Token", f"Expected 'Simple Token', got {name}"
        
        print_success("icrc1_name tests passed")
        return True
    except Exception as e:
        print_failure("icrc1_name tests failed", str(e))
        return False


def test_icrc1_symbol():
    """Test icrc1_symbol query"""
    try:
        from main import icrc1_symbol
        
        symbol = icrc1_symbol()
        assert symbol == "SMPL", f"Expected 'SMPL', got {symbol}"
        
        print_success("icrc1_symbol tests passed")
        return True
    except Exception as e:
        print_failure("icrc1_symbol tests failed", str(e))
        return False


def test_icrc1_decimals():
    """Test icrc1_decimals query"""
    try:
        from main import icrc1_decimals
        
        decimals = icrc1_decimals()
        assert decimals == 8, f"Expected 8, got {decimals}"
        
        print_success("icrc1_decimals tests passed")
        return True
    except Exception as e:
        print_failure("icrc1_decimals tests failed", str(e))
        return False


def test_icrc1_fee():
    """Test icrc1_fee query"""
    try:
        from main import icrc1_fee
        
        fee = icrc1_fee()
        assert fee == 10_000, f"Expected 10000, got {fee}"
        
        print_success("icrc1_fee tests passed")
        return True
    except Exception as e:
        print_failure("icrc1_fee tests failed", str(e))
        return False


def test_token_helper_balance():
    """Test TokenHelper balance operations"""
    try:
        from main import TokenHelper
        
        # Test initial balance (should be 0)
        balance = TokenHelper.get_balance("test-user-1")
        assert balance == 0, f"Expected 0, got {balance}"
        
        # Set balance
        TokenHelper.set_balance("test-user-1", 1000)
        balance = TokenHelper.get_balance("test-user-1")
        assert balance == 1000, f"Expected 1000, got {balance}"
        
        # Update balance
        TokenHelper.set_balance("test-user-1", 500)
        balance = TokenHelper.get_balance("test-user-1")
        assert balance == 500, f"Expected 500, got {balance}"
        
        print_success("token_helper_balance tests passed")
        return True
    except Exception as e:
        print_failure("token_helper_balance tests failed", str(e))
        return False


def test_token_helper_supply():
    """Test TokenHelper supply operations"""
    try:
        from main import TokenHelper
        
        # Set total supply
        TokenHelper.set_total_supply(1_000_000_000)
        supply = TokenHelper.get_total_supply()
        assert supply == 1_000_000_000, f"Expected 1000000000, got {supply}"
        
        # Update supply
        TokenHelper.set_total_supply(999_999_000)
        supply = TokenHelper.get_total_supply()
        assert supply == 999_999_000, f"Expected 999999000, got {supply}"
        
        print_success("token_helper_supply tests passed")
        return True
    except Exception as e:
        print_failure("token_helper_supply tests failed", str(e))
        return False


def test_icrc1_metadata():
    """Test icrc1_metadata query"""
    try:
        from main import icrc1_metadata
        
        metadata = icrc1_metadata()
        assert len(metadata) == 4, f"Expected 4 metadata entries, got {len(metadata)}"
        
        # Check metadata contains expected keys
        metadata_dict = dict(metadata)
        assert "icrc1:name" in metadata_dict
        assert "icrc1:symbol" in metadata_dict
        assert "icrc1:decimals" in metadata_dict
        assert "icrc1:fee" in metadata_dict
        
        print_success("icrc1_metadata tests passed")
        return True
    except Exception as e:
        print_failure("icrc1_metadata tests failed", str(e))
        return False


def test_icrc1_supported_standards():
    """Test icrc1_supported_standards query"""
    try:
        from main import icrc1_supported_standards
        
        standards = icrc1_supported_standards()
        assert len(standards) >= 1, f"Expected at least 1 standard, got {len(standards)}"
        
        # Check ICRC-1 is supported
        standards_dict = dict(standards)
        assert "ICRC-1" in standards_dict
        
        print_success("icrc1_supported_standards tests passed")
        return True
    except Exception as e:
        print_failure("icrc1_supported_standards tests failed", str(e))
        return False


def run_tests():
    """Run all tests and report results"""
    print(f"{BOLD}Running Token Backend Tests...{RESET}\n")

    success_count = 0
    failure_count = 0

    tests = [
        test_token_constants,
        test_icrc1_name,
        test_icrc1_symbol,
        test_icrc1_decimals,
        test_icrc1_fee,
        test_token_helper_balance,
        test_token_helper_supply,
        test_icrc1_metadata,
        test_icrc1_supported_standards,
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
