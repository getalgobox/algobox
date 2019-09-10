import inspect
import collections

from abc import ABC, abstractmethod

import ffn
import requests

import numpy as np

import core

from core.backtest import data_handler
from core.exceptions import NoMoreData


class AlgoBoxBacktestManager(ABC):
    """
    This is the class that will drive the backtest.

    It knows only the id of the strategy it will call, nothing about the
    code it will execute, which will be handled by another service.

    This class will also be responsible for updating the account instance
    and observer instance, which will provide reporting statistics.


    !TODO think of a name for the push_update property which makes more sense
    for the user driven script scenario. One option is
    to create a seperate child class to make working with the BacktestManager
    more intuitive for a user who would like to use core as a library.

    Arguments:
        * topic (string) the 'key' of the data the backtest will use; the
            data it cares about.
        * dt_from (datetime.datetime) when to start the backtest
        * dt_to (datetime.datetime) when to end the backtest
        * strat_id (uuid, string) The ID of the strategy according to the algo
            service.
        * lookback_period (number)of previous data updates to
            include as context.
        * data (list)or generator; produces or contains instances of
            ABDataFormat instances. Currently we only support Candle. If this
            param is not provided data will be queried from the market data
            store (not yet implemented). !TODO

    Attributes:
        * topic (string, const.topic.Topic) the topic string for this backtest,
            in the following format: `exchange:asset:interval` or a
            const.topic.Topic() instance.
        * start (datetime.datetime) when to start the backtest
        * end (datetime.datetime) when to end the backtest
        * strat_id (uuid, string)
        * lookback_period (integer) number of previous updates to
            provide as historical context for the strategy
            (will be renamed lookback_length)
        * strat_service_uri (string) the uri for the strategy service
        * strat_uuid_uri (string) full uri for the strategy
        * on_open_actions (deque) events which should be acted on next tick.
            For example, given a backtest / real strategy with 5M candles:
            At 10:00, the strategy decides to produce a signal having just
            recieved OHCLV for period 9:55-10:00. The price at close is no
            longer available. The actual signal needs to be executed in
            10:00-10:05 period at open. The BacktestManager currently uses
            the open price of this period.
        * push_update (function) a function used to 'push' updates from the
            data_handler to a strategy and retrieve a signal in response.
            Can be user provided or one of:
            BacktestManager._pusher_strategy_service,
            BacktestManager._pusher_dry,
            BacktestManager._pusher_dry_random
            This property is confusing if looking at algobox from a library
            standpoint as opposed to a systems standpoint. We should encapuslate
            this behaviour in seperate classes. !TODO

    """

    def __init__(self, topic, dt_from, dt_to, lookback_period=30,
        data=None, strat_service_uri=None, starting_balance = 10000):

        self.complete = False

        self.topic = core.topic.Topic(topic)
        self.start = dt_from
        self.end = dt_to
        self.lookback_period = lookback_period

        self.account = core.backtest.account.BacktestAccount(starting_balance)
        self.observer = core.reporting.observer.ABObserver()

        # a list of actions which must be performed on the next iteration
        # trades will be executed at the next candles open price and thus
        # will sit in this queue until the next candle is retrieved

        self.on_open_actions = collections.deque()

        if data and isinstance(data, list):
            self.data_handler = data_handler.ListDataHandler(
                data, lookback_period
            )
        elif data and inspect.isgenerator(data) or hasattr(data, "__next__"):
            self.data_handler = data_handler.GeneratorHandler(
                data, lookback_period
            )
        else:
            raise NotImplementedError("No data was provided, we do not currently \
            support retrieving this from a database. Please provide the `data` \
            parameter. See docs/help.")

        self.previous_dt = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.account.bankrupt:
                bankrupt_event = core.event.ABEvent(
                    type=core.const.Event.BANKRUPT_ACCOUNT,
                    datetime=self.previous_dt
                )
                self.observer.update(bankrupt_event)
                raise NoMoreData
            # retrieve next set
            context, update = self.data_handler.next()

            # handle order to be executed now
            # !TODO test transactions are made
            while self.on_open_actions:
                action = self.on_open_actions.pop()
                if action.type == core.const.Event.SIGNAL_BUY:
                    self.observer.update(core.event.ABEvent(
                        type=core.const.Event.TRANSACTION_BUY,
                        datetime=update.datetime
                        )
                    )
                    self.account.purchase(self.topic.asset, update.open)
                elif action.type == core.const.Event.SIGNAL_SELL:
                    self.observer.update(core.event.ABEvent(
                        type=core.const.Event.TRANSACTION_SELL,
                        datetime=update.datetime
                        )
                    )
                    self.account.sell(self.topic.asset, update.open)

            # push the context and update to the strategy* and retrieve signal
            # *: may be the strategy or one of the
            # BacktestManager._dry_push_* methods

            signal = self.push_update(context, update)

            if signal in core.const.Event.SIGNAL_ACTIONABLE:
                # update.datetime represents the current time in our backtest
                event_signal = core.event.ABEvent(type=signal, datetime=update.datetime)
                self.on_open_actions.append(event_signal)
                self.observer.update(event_signal)

            price_update_event = core.event.ABEvent(
                type=core.const.Event.PRICE_UPDATE,
                data=update.close,
                datetime=update.datetime
            )

            equity_update_event = core.event.ABEvent(
                type=core.const.Event.EQUITY_UPDATE,
                data=self.account.calculate_equity(update.close),
                datetime=update.datetime
            )

            cash_update_event = core.event.ABEvent(
                type=core.const.Event.CASH_UPDATE,
                data=self.account.balance,
                datetime=update.datetime
            )

            # this should happen last, after any trades have executed
            self.observer.update(price_update_event)
            self.observer.update(equity_update_event)
            self.observer.update(cash_update_event)
            self.previous_dt = update.datetime

        except NoMoreData:
            self.complete = True
            raise StopIteration

        return context, update

    def pusher_factory(self, user_strategy, additional_imports=[]):
        """
        Used for creating a pusher for your local strategy. Returns a function
        with the correct contexts for assigning to `BacktestManager.pusher`
        Used in running local backtests for local strategies.

        Arguments:
            * user_strategy (core.strategy.ABStrategy) user defined strat
            * additional_imports (list[string]) list of additional modules
                you would like in your strategy execution environment.
                See source of core.strategy.execute to see already included
                modules.

        Returns:
            * pusher_method (function) this method will 'push' data to your
                strategy and returns the signal your strategy generates
        """

        def user_pusher(context, update):
            signal = core.strategy.execute(
                strategy_class=user_strategy,
                context=context,
                update=update,
                additional_imports=additional_imports,
                lookback_period=self.lookback_period,
            )

            return signal["signal"]

        return user_pusher

        def _pusher_dry(self, context, update):
            """
            Don't update any strategy for a signal; return SIGNAL_NO_ACTION.
            """
            return {"signal": core.const.Event.SIGNAL_NO_ACTION}["signal"]

        def _pusher_dry_random(self, context, update):
            """
            Doesn't push any data, returns a random signal.
            """
            return {"signal": core.signal.random()}["signal"]

        def finalise(self):
            """
            Finalise the backtest, generate ffn report.
            """
            backtest_series, events = self.observer.retrieve()
            performance = backtest_series.calc_stats()
            return performance

class LocalBacktestManager(AlgoBoxBacktestManager):
    def __init__(
        self, topic, dt_from, dt_to, user_strategy, lookback_period=30, data=None,
         starting_balance=10000, additional_strategy_imports=None
        ):
        AlgoBoxBacktestManager.__init__(data=data)
        self.push_update = self.pusher_factory(
            user_strategy=user_strategy,
            additional_strategy_imports=additional_strategy_imports
        )

class RemoteBacktestManager(AlgoBoxBacktestManager):
    def __init__(
        self, topic, dt_from, dt_to, strat_id, lookback_period=30,
        starting_balance=10000, data=None, strat_service_uri=None,
        ):
        AlgoBoxBacktestManager.__init__()

        self.strat_id = str(strat_id)
        self.strat_service_uri = strat_service_uri or "http://algoservice:5550"
        self.strat_service_uri = self.strat_service_uri + "/" + self.strat_id
        self.push_update = self._pusher_strategy_service


    def _pusher_strategy_service(self, context, update):
        """
        This method will push the new update to the AlgoBox strategy_service.
        If you would like to push updates to a local Strategy see
        `BacktestManager.pusher_factory`.

        Upon receiving a response, it will attempt to marshall it from JSON.
        It will return the signal key from this json.

        The other 'pushers' do not really push to the service, but simulate that.
        They allow this class to be used as an independent backtester.
        """
        d = {
            "context": [candle.to_dict() for candle in context],
            "update": update.to_dict(),
            "topic": self.topic
        }

        response = requests.post(self.strat_service_uri, json=d)

        if response.status_code not in [200, 201]:
            raise ValueError("Something went wrong when pushing the update to \
            the Strategy Service.")

        return json.loads(response.text)["signal"]



class MultiAssetBacktestManager(BacktestManager):
    """
    """
    pass
