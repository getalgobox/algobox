import pytest
from core.backtest.account import BacktestAccount

@pytest.fixture
def account():
    return BacktestAccount(starting_balance=10000)

def test_backtest_account(account):
    account.purchase("LLOY", 100)

    assert account.holdings["LLOY"] == 100.0
    assert account.balance == 0.0
    assert account.calculate_equity(100) == 10000

    account.set_balance(5000)

    assert account.balance == 5000.0
    assert account.calculate_equity(100) == 15000

    account.sell("LLOY", 100)

    assert account.balance == 15000

    account.set_balance(0)

    assert account.balance == 0
    assert account.is_bankrupt
