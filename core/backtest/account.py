#!TODO <rounding>
import collections

from abc import ABC, abstractmethod

class BacktestAccount(object):
    """
    Tracks the things your broker would usually track. Your balance and assets
    held.
    """

    def __init__(self, starting_balance):
        self.balance = starting_balance
        self.holdings = collections.defaultdict(int)
        self.balance_series = [starting_balance]

    def set_balance(self, balance):
        self.balance = balance

    @property
    def holdings_total(self):
        """
        The total quantity of assets owned
        """
        total_asset_count = 0
        for _, v in self.holdings.items():
            total_asset_count += v
        return total_asset_count

    @property
    def is_bankrupt(self):
         return (balance < 1 and self.total_asset_count == 0)

    def calculate_equity(self, latest_asset_price):
        # assumes BacktestManager is only tracking one asset, we iterate because
        # we don't know the name of the asset and it doesn't matter, there should
        # only be one
        equity_value = latest_asset_price * self.total_asset_count

        return self.balance + equity_value

    def purchase(self, asset, latest_price):
        """
        Backtest assumes max quantity of assets purchased. It also assumes that
        orders are filled at the price given.
        """
        current_cash = self.balance
        quantity_to_purchase =  int(current_cash / latest_price)
        cost_to_purchase = quantity_to_purchase * latest_price

        self.holdings[asset] = quantity_to_purchase
        self.balance = self.balance - cost_to_purchase

    def sell(self, asset, latest_price):
        """
        Backtest assumes max quantity of assets sold. It also assumes that
        orders are filled at the price given.
        """
        current_cash = self.balance
        quantity_to_sell = self.holdings[asset]
        proceeds_of_sale = quantity_to_sell * latest_price

        self.holdings[asset] = self.holdings[asset] - quantity_to_sell
        self.balance = self.balance + proceeds_of_sale
