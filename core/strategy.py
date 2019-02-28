import importlib

from abc import ABC
from abc import abstractmethod

import core
from core.exceptions import AlgoBoxUserStrategyException

class ABStrategy(ABC):
    """
    The strategy class used by AlgoBox.

    Arguments:
        * lookback_period (integer) defaults to 30. Should be used to check the
            lookback setting. In backtests, this is set by the BacktestManager.
            The strategy should ideally ensure that it can operate on any
            lookback period.

            Note that on_data will not be called until we have sufficient
            history for the full lookback period.
    """

    def __init__(self, lookback_period=30):
        self.lookback_period = lookback_period

    def initialise(self):
        """
        Some user provided initalisation
        """
        pass

    @abstractmethod
    def on_data(self, context, update):
        """
        Handles new data provided from some source.

        Arguments:
            * context (list) of core.format.Candle. Previous market updates
            * update (core.format.Candle), this market update

        Returns:
            * signal (dictionary) with key of 'signal' where the value is one of:
                core.const.Event.BUY_SIGNAL, core.const.Event.SELL_SIGNAL,
                core.const.Event.SIGNAL_NO_ACTION.
                The strategy MUST always return this dictionary.
        """
        pass

    def _handle_update(self, context, update):
        """
        Wraps on_data with context and update but raises
        core.exceptions.AlgoBoxUserStrategyException if the signal is incorrect.
        """
        user_strat_exception = AlgoBoxUserStrategyException("""

        AlgoBoxUserStrategyException: on_data must always return a signal
        with key of 'signal' where the value is one of:
            core.const.Event.BUY_SIGNAL, core.const.Event.SELL_SIGNAL,
            core.const.Event.SIGNAL_NO_ACTION.

        if there is no action to be performed, return
        {"signal": core.const.Event.SIGNAL_NO_ACTION}

        """)

        res = self.on_data(context, update)


        if not res:
            raise user_strat_exception

        if "signal" not in res:
            raise user_strat_exception

        if res["signal"] not in [core.const.Event.SIGNAL_BUY,
            core.const.Event.SIGNAL_SELL, core.const.Event.SIGNAL_NO_ACTION]:
            raise user_strat_exception

        return res


def execute_strategy(strategy_class, context, update, additional_imports=[], lookback_period=30):
    """
    This function will setup the Python Context for the strategy instance,
    execute it and return the result to the caller.

    Arguments:
        * strategy_class (core.strategy.ABStrategy child) the user defined
            strategy class.
    """
    import datetime as dt
    import pandas as pd
    import numpy as np
    import ffn

    for module_name in additional_imports:
        importlib.import_module(module_name)

    strat = strategy_class()
    strat.initialise()
    result = strat._handle_update(context, update)
    return result
