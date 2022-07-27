from eth_utils import to_checksum_address, to_canonical_address
import pytest
import boa
from boa.contract import BoaError
from hypothesis import settings, example, given, strategies as st

boa.interpret.set_cache_dir()

ONE = 10**18

# util to get checksum address
def address(t):
    return to_checksum_address(t.rjust(40, "0"))

@pytest.fixture(scope="session")
def erc20():
    return boa.load("contracts/ERC20.vy", boa.env.eoa, "Token", "TKN", 18)

@pytest.fixture()
def token(erc20):
    with boa.env.anchor():
        yield erc20

@pytest.fixture()
def beef():
    return address("beef")

def test_mint(token, beef):
    token.mint(beef, ONE)

    assert token.totalSupply() == ONE
    assert token.balanceOf(beef) == ONE

def test_burn(token, beef):
    token.mint(beef, ONE)
    token.burn(beef, int(0.9e18))

    assert token.totalSupply() == int(0.1e18)
    assert token.balanceOf(beef) == int(0.1e18)

def test_approve(token, beef):
    assert token.approve(beef, ONE) is True
    assert token.allowance(boa.env.eoa, beef) == ONE

def test_transfer(token, beef):
    token.mint(boa.env.eoa, ONE)

    assert token.transfer(beef, ONE) is True
    assert token.totalSupply() == ONE

    assert token.balanceOf(boa.env.eoa) == 0
    assert token.balanceOf(beef) == ONE

def test_transferFrom(token, beef):
    sender = address("abcd")

    token.mint(sender, ONE)

    this = boa.env.eoa
    with boa.env.prank(sender):
        token.approve(this, ONE)

    assert token.transferFrom(sender, beef, ONE) is True
    assert token.totalSupply() == ONE

    assert token.allowance(sender, boa.env.eoa) == 0

    assert token.balanceOf(sender) == 0
    assert token.balanceOf(beef) == ONE

def test_infinite_approve_transferFrom(token, beef):
    sender = address("abcd")

    token.mint(sender, ONE)

    this = boa.env.eoa
    with boa.env.prank(sender):
        token.approve(this, 2**256 - 1)

    assert token.transferFrom(sender, beef, ONE) is True
    assert token.totalSupply() == ONE

    assert token.allowance(sender, boa.env.eoa) == 2**256 - 1

    assert token.balanceOf(sender) == 0
    assert token.balanceOf(beef) == ONE

@pytest.mark.xfail()
def test_fail_transfer_insufficient_balance(token, beef):
    token.mint(boa.env.eoa, int(0.9e18))
    token.transfer(beef, ONE)


@pytest.mark.xfail()
def test_fail_transferFrom_insufficient_allowance(token, beef):
    sender = address("abcd")
    token.mint(sender, ONE)
    token.approve(boa.env.eoa, int(0.9e18))

    token.transferFrom(sender, beef, ONE)


@pytest.mark.xfail()
def test_fail_transferFrom_insufficient_balance(token, beef):
    sender = address("abcd")
    token.mint(sender, int(0.9e18))
    token.approve(boa.env.eoa, ONE)

    token.transferFrom(sender, beef, ONE)


MAX_UINT256 = 2 ** 256 - 1
@given(st.binary(max_size=20), st.integers(min_value=0, max_value=MAX_UINT256))
@example(recipient=boa.env.eoa, amount=0)
@example(recipient=boa.env.eoa, amount=MAX_UINT256)
@example(recipient=boa.env.eoa, amount=1)
@settings(max_examples=256)
def test_transfer_fuzzing(erc20, recipient, amount):
    if isinstance(recipient, bytes):
        recipient = to_checksum_address(recipient.rjust(20, b"\x00"))

    with boa.env.anchor():
        token = erc20
        token.mint(boa.env.eoa, amount)

        assert token.transfer(recipient, amount) is True
        assert token.totalSupply() == amount

        if recipient == boa.env.eoa:
            assert token.balanceOf(boa.env.eoa) == amount
        else:
            assert token.balanceOf(boa.env.eoa) == 0
            assert token.balanceOf(recipient) == amount
