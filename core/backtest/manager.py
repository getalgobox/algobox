import inspect
import collections

import ffn
import requests

import core

from core.backtest import data_handler
from core.exceptions import NoMoreData


class BacktestManager(object):
    """
    This is the class that will drive the backtest.

    It knows only the id of the algorithm it will call, nothing about the
    code it will execute, which will be handled by another service.

    This class will also be responsible for updating the account instance
    and observer instance, which will provide reporting statistics.

    Arguments:
        * topic (string) the 'key' of the data the backtest will use; the
            data it cares about.
        * dt_from (datetime.datetime) when to start the backtest
        * dt_to (datetime.datetime) when to end the backtest
        * algo_id (uuid, string) The ID of the algorithm according to the algo
            service.
        * historical_context_number (number)of previous data updates to
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
        * algo_id (uuid, string)
        * historical_context_number (integer) number of previous updates to
            provide as historical context for the algorithm
            (will be renamed lookback_length)
        * algo_service_uri (string) the uri for the algorithm service
        * algo_uuid_uir (string) full uri for the algorithm
        * on_open_actions (deque) events which should be acted on next tick.
            For example, given a backtest / real algorithm with 5M candles:
            At 10:00, the algorithm decides to produce a signal having just
            recieved OHCLV for period 9:55-10:00. The price at close is no
            longer available. The actual signal needs to be executed in
            10:00-10:05 period at open. The BacktestManager currently uses
            the open price of this period.
    """

    def __init__(self, topic, dt_from, dt_to, algo_id, historical_context_number=30,
        data=None, algo_service_uri=None, starting_balance = 10000):

        self.topic = core.topic.Topic(topic)
        self.start = dt_from
        self.end = dt_to
        self.algo_id = str(algo_id)
        self.historical_context_number = historical_context_number

        self.algo_service_uri = algo_service_uri or "http://algoservice:5550"
        self.algo_uuid_uri = self.algo_service_uri + "/" + self.algo_id

        self.account = core.backtest.account.BacktestAccount(starting_balance)
        self.observer = core.reporting.observer.ABObserver()

        # a list of actions which must be performed on the next iteration
        # trades will be executed at the next candles open price and thus
        # will sit in this queue until the next candle is retrieved

        self.on_open_actions = collections.deque()

        if data and isinstance(data, list):
            self.data_handler = data_handler.ListDataHandler(
                data, historical_context_number
            )
        elif data and inspect.isgenerator(data) or hasattr(data, "__next__"):
            self.data_handler = data_handler.GeneratorHandler(
                data, historical_context_number
            )
        else:
            raise NotImplementedError("No data was provided, we do not currently \
            support retrieving this from a database. Please provide the `data` \
            parameter. See docs/help.")

        self.push_update = self._push_update

    def __iter__(self):
        return self

    def __next__(self):
        try:
            # retrieve next set
            context, update = self.data_handler.next()

            # handle order to be executed now
            while self.on_open_actions:
                action = self.on_open_actions.pop()
                if action.type == core.const.Event.SIGNAL_BUY:
                    self.observer.update(core.event.ABEvent(
                        type=core.const.TRANSACTION_BUY,
                        data=update.open,
                        datetime=update.datetime
                        )
                    )
                    self.account.purchase(self.topic.asset, update.open)
                elif action.type == core.const.Event.SIGNAL_SELL:
                    self.observer.update(core.event.ABEvent(
                        type=core.const.TRANSACTION_SELL,
                        data=update.open,
                        datetime=update.datetime
                        )
                    )
                    self.account.sell(self.topic.asset, update.open)


            signal = self.push_update(context, update)

            if signal in core.const.Event.SIGNAL_ACTIONABLE:
                # update.datetime represents the current time in our backtest
                signal = core.event.ABEvent(signal, {}, update.datetime)
                self.on_open_actions.append(signal)

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

            # this should happen last, after any trades have executed
            self.observer.update(price_update_event)
            self.observer.update(equity_update_event)

        except NoMoreData:
            self._finalise()
            raise StopIteration
        return context, update


    def _push_update(self, context, update):
        """
        This method will push the new update to the algorithm we are testing.
        Upon receiving a response, it will attempt to marshall it from JSON.
        It will return the signal key from this json.
        """
        d = {
            "context": [candle.to_dict() for candle in context],
            "update": update.to_dict()
        }
        response = requests.post(self.algo_service_uri, json=d)

        if response.status_code not in [200, 201]:
            raise ValueError("Something went wrong when pushing the update to \
            the AlgoService.")

        return json.loads(response.text)["signal"]

    def _dry_push_update(self, context, update):
        """
        Don't update any algorithm for a signal.
        """
        return {"signal": core.const.Event.SIGNAL_NO_ACTION}

    def finalise(self):
        """
        Finalise the backtest, generate ffn report.
        """
        pass

class MultiAssetBacktestManager(BacktestManager):
    """
    """
    pass
