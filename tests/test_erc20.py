from eth_utils import to_checksum_address
import pytest
import boa
from boa.contract import BoaError

boa.interpret.set_cache_dir()

ONE = 10**18

# util to get checksum address
def address(t):
    return to_checksum_address(t.rjust(40, "0"))

@pytest.fixture()
def token():
    return boa.load("contracts/ERC20.vy", boa.env.eoa, "Token", "TKN", 18)

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
