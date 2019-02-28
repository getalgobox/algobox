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
    def bankrupt(self):
         return (self.balance < 1 and self.holdings_total == 0)

    def set_balance(self, balance):
        self.balance = balance

    def calculate_equity(self, latest_asset_price):
        # assumes BacktestManager is only tracking one asset, we iterate because
        # we don't know the name of the asset and it doesn't matter, there should
        # only be one
        equity_value = latest_asset_price * self.holdings_total

        return self.balance + equity_value

    def purchase(self, asset, latest_price):
        """
        Backtest assumes max quantity of assets purchased. It also assumes that
        orders are filled at the price given.
        """
        current_cash = self.balance
        quantity_to_purchase =  current_cash / latest_price

        if quantity_to_purchase < 1:
            return
        quantity_to_purchase = int(quantity_to_purchase)

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

        if quantity_to_sell <= 0:
            return

        self.holdings[asset] = self.holdings[asset] - quantity_to_sell
        self.balance = self.balance + proceeds_of_sale
