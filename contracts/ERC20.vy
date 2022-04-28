# @version >=0.3.2

from vyper.interfaces import ERC20


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256


event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256


NAME: immutable(String[32])
SYMBOL: immutable(String[32])
DECIMALS: immutable(uint8)
MINTER: immutable(address)

totalSupply: public(uint256)

balanceOf: public(HashMap[address, uint256])

allowance: public(HashMap[address, HashMap[address, uint256]])

@external
def __init__(minter: address, name: String[32], symbol: String[32], decimals: uint8):
    MINTER = minter
    NAME = name
    SYMBOL = symbol
    DECIMALS = decimals


@internal
def _transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    self.allowance[sender][msg.sender] -= amount

    self.balanceOf[sender] -= amount

    # Cannot overflow because the sum of all user
    # balances can't exceed MAX_UINT256
    self.balanceOf[receiver] = unsafe_add(amount, self.balanceOf[receiver])

    log Transfer(sender, receiver, amount)

    return True


@external
def transfer(receiver: address, amount: uint256) -> bool:
    return self._transferFrom(msg.sender, receiver, amount)


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    return self._transferFrom(sender, receiver, amount)


@external
def approve(spender: address, amount: uint256) -> bool:
    self.allowance[msg.sender][spender] = amount
    log Approval(msg.sender, spender, amount)
    return True


@external
def mint(receiver: address, amount: uint256) -> bool:
    assert MINTER == msg.sender

    self.totalSupply += amount
    # can unsafe_add because balanceOf[receiver] <= totalSupply
    self.balanceOf[receiver] = unsafe_add(amount, self.balanceOf[receiver])

    log Transfer(empty(address), receiver, amount)
    return True


# TODO: generate getters automatically
@view
@external
def name() -> String[32]:
    return NAME


@view
@external
def symbol() -> String[32]:
    return SYMBOL


@view
@external
def decimals() -> uint8:
    return DECIMALS
