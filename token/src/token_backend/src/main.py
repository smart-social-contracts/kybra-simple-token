from kybra import (
    Opt,
    Principal,
    Record,
    StableBTreeMap,
    Tuple,
    Vec,
    blob,
    ic,
    init,
    nat,
    nat8,
    query,
    text,
    update,
    void,
)
from kybra_simple_db import Database, Entity, Integer, String
from kybra_simple_logging import get_logger

# Initialize stable storage for the database
storage = StableBTreeMap[str, str](memory_id=1, max_key_size=200, max_value_size=100_000)
Database.init(db_storage=storage, audit_enabled=True)

logger = get_logger("token")


# Database Entity for storing balances
class TokenBalance(Entity):
    __alias__ = "id"
    id = String()
    amount = Integer()


# Database Entity for storing token metadata
class TokenConfig(Entity):
    __alias__ = "key"
    key = String()
    value = String()


# Register entity types
Database.get_instance().register_entity_type(TokenBalance)
Database.get_instance().register_entity_type(TokenConfig)


# ICRC-1 Types
MetadataEntry = Tuple[text, text]


class Account(Record):
    owner: Principal
    subaccount: Opt[blob]


class TransferArgs(Record):
    from_subaccount: Opt[blob]
    to: Account
    amount: nat
    fee: Opt[nat]
    memo: Opt[blob]
    created_at_time: Opt[nat]


class TransferResult(Record):
    success: bool
    block_index: Opt[nat]
    error: Opt[text]


class MintArgs(Record):
    to: Account
    amount: nat


class MintResult(Record):
    success: bool
    new_balance: Opt[nat]
    error: Opt[text]


class TokenMetadataRecord(Record):
    name: text
    symbol: text
    decimals: nat8
    fee: nat
    total_supply: nat


# Token configuration
TOKEN_NAME = "Simple Token"
TOKEN_SYMBOL = "SMPL"
TOKEN_DECIMALS: nat8 = 8
TOKEN_FEE: nat = 10_000


class TokenHelper:
    @staticmethod
    def get_account_key(owner, subaccount=None):
        sub = subaccount.hex() if subaccount else "default"
        return f"{owner}:{sub}"

    @staticmethod
    def get_balance(owner, subaccount=None):
        key = TokenHelper.get_account_key(owner, subaccount)
        balance = TokenBalance[key]
        if balance:
            return balance.amount or 0
        return 0

    @staticmethod
    def set_balance(owner, balance_amount, subaccount=None):
        key = TokenHelper.get_account_key(owner, subaccount)
        balance = TokenBalance[key]
        if balance:
            balance.amount = balance_amount
            balance.save()
        else:
            TokenBalance(id=key, amount=balance_amount)

    @staticmethod
    def get_total_supply():
        config = TokenConfig["total_supply"]
        if config and config.value:
            return int(config.value)
        return 0

    @staticmethod
    def set_total_supply(supply):
        config = TokenConfig["total_supply"]
        if config:
            config.value = str(supply)
            config.save()
        else:
            TokenConfig(key="total_supply", value=str(supply))


class OwnerHelper:
    @staticmethod
    def get_owner():
        config = TokenConfig["owner"]
        if config and config.value:
            return config.value
        return None

    @staticmethod
    def set_owner(owner):
        config = TokenConfig["owner"]
        if config:
            config.value = owner
            config.save()
        else:
            TokenConfig(key="owner", value=owner)

    @staticmethod
    def is_owner(principal):
        return principal == OwnerHelper.get_owner()


@init
def init_() -> void:
    logger.info("Initializing token canister")
    initial_supply = 1_000_000_000 * (10 ** TOKEN_DECIMALS)
    deployer = ic.caller().to_str()
    OwnerHelper.set_owner(deployer)
    TokenHelper.set_balance(deployer, initial_supply)
    TokenHelper.set_total_supply(initial_supply)
    logger.info(f"Token initialized. Initial supply: {initial_supply} to {deployer}")


@query
def icrc1_name() -> text:
    return TOKEN_NAME


@query
def icrc1_symbol() -> text:
    return TOKEN_SYMBOL


@query
def icrc1_decimals() -> nat8:
    return TOKEN_DECIMALS


@query
def icrc1_fee() -> nat:
    return TOKEN_FEE


@query
def icrc1_total_supply() -> nat:
    return TokenHelper.get_total_supply()


@query
def icrc1_minting_account() -> Opt[Account]:
    return None


@query
def icrc1_balance_of(account: Account) -> nat:
    owner_str = account.owner.to_str()
    return TokenHelper.get_balance(owner_str, account.subaccount)


@query
def icrc1_metadata() -> Vec[MetadataEntry]:
    return [
        ("icrc1:name", TOKEN_NAME),
        ("icrc1:symbol", TOKEN_SYMBOL),
        ("icrc1:decimals", str(TOKEN_DECIMALS)),
        ("icrc1:fee", str(TOKEN_FEE)),
    ]


@query 
def icrc1_supported_standards() -> Vec[MetadataEntry]:
    return [
        ("ICRC-1", "https://github.com/dfinity/ICRC-1"),
    ]


@update
def icrc1_transfer(args: TransferArgs) -> TransferResult:
    caller = ic.caller().to_str()
    logger.info(f"Transfer request: {caller} -> {args.to.owner.to_str()}, amount: {args.amount}")
    
    sender_balance = TokenHelper.get_balance(caller, args.from_subaccount)
    fee = args.fee if args.fee is not None else TOKEN_FEE
    total_deduction = args.amount + fee
    
    if sender_balance < total_deduction:
        logger.warning(f"Insufficient balance: {sender_balance} < {total_deduction}")
        return TransferResult(
            success=False,
            block_index=None,
            error=f"Insufficient balance. Have {sender_balance}, need {total_deduction}"
        )
    
    recipient = args.to.owner.to_str()
    recipient_balance = TokenHelper.get_balance(recipient, args.to.subaccount)
    
    TokenHelper.set_balance(caller, sender_balance - total_deduction, args.from_subaccount)
    TokenHelper.set_balance(recipient, recipient_balance + args.amount, args.to.subaccount)
    
    current_supply = TokenHelper.get_total_supply()
    TokenHelper.set_total_supply(current_supply - fee)
    
    logger.info(f"Transfer successful: {args.amount} tokens transferred")
    
    return TransferResult(
        success=True,
        block_index=1,
        error=None
    )


@update
def mint(args: MintArgs) -> MintResult:
    caller = ic.caller().to_str()
    logger.info(f"Mint request from {caller}: {args.amount} to {args.to.owner.to_str()}")
    
    if not OwnerHelper.is_owner(caller):
        logger.warning(f"Unauthorized mint attempt by {caller}")
        return MintResult(
            success=False,
            new_balance=None,
            error="Only the token owner can mint tokens"
        )
    
    recipient = args.to.owner.to_str()
    current_balance = TokenHelper.get_balance(recipient, args.to.subaccount)
    new_balance = current_balance + args.amount
    
    TokenHelper.set_balance(recipient, new_balance, args.to.subaccount)
    
    current_supply = TokenHelper.get_total_supply()
    TokenHelper.set_total_supply(current_supply + args.amount)
    
    logger.info(f"Minted {args.amount} tokens to {recipient}. New balance: {new_balance}")
    
    return MintResult(
        success=True,
        new_balance=new_balance,
        error=None
    )


@query
def get_owner() -> text:
    owner = OwnerHelper.get_owner()
    return owner if owner else ""


@query
def get_token_info() -> TokenMetadataRecord:
    return TokenMetadataRecord(
        name=TOKEN_NAME,
        symbol=TOKEN_SYMBOL,
        decimals=TOKEN_DECIMALS,
        fee=TOKEN_FEE,
        total_supply=TokenHelper.get_total_supply()
    )


@query
def get_my_balance() -> nat:
    return TokenHelper.get_balance(ic.caller().to_str())


@query
def get_my_principal() -> text:
    return ic.caller().to_str()
