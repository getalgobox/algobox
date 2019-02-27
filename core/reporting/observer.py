import core

class ABObserver(object):
    """
    ABObserver stores information which outside of the backtest,
    would be apparent from our timeseries store and database.
    """
    event_handler_map = {
        core.const.Event.PRICE_UPDATE: self._handle_asset_price,
        core.const.Event.EQUITY_UPDATE: self._handle_equity_update,
        core.const.Event.TRANSACTION_BUY: self._handle_event,
        core.const.Event.TRANSACTION_SELL: self._handle_event,
    }

    def __init__(self):
        self.equity_series = []
        self.asset_price_series = []
        self.event_series = []

    def update(self, event):
        event_handler_map[event.type](data)

    def _handle_asset_price(self, price):
        self.asset_price_series.append(price)

    def _handle_equity_update(self, equity):
        self.equity_series.append(price)

    def _handle_event(self, event):
        self.event_series.append(event)
