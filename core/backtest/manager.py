import inspect

import core

from core.backtest import data_handler
from core.exceptions import NoMoreData


class BacktestManager(object):

    def __init__(self, topic, dt_from, dt_to, algo_id, historical_context_number=30,
        data=None, algo_service_uri=None):
        """
        This is the class that will drive the backtest.

        It knows only the id of the algorithm it will call, nothing about the
        code it will execute, which will be handled by another service.

        :param topic: string; the 'key' of the data the backtest will use. The
         data it cares about.
        :param dt_from: datetime; when to start the backtest
        :param dt_to: datetime; when to end the backtest
        :algo_id: uuid, string; The ID of the algorithm according to the algo
         service.
        :param historical_context_number: number of previous data updates to
         include as context.
        :param data: list or generator; produces or contains instances of
         ABDataFormat instances. Currently we only support Candle. If this param
         is not provided data will be queried from the TSDB (tbd) !TODO.
        """

        self.topic = topic
        self.start = dt_from
        self.end = dt_to
        self.algo_id = algo_id
        self.historical_context_number = historical_context_number
        self.algo_service_uri = algo_service_uri or "http://algoservice:5550"

        if data and isinstance(data, list):
            self.list_handler = data_handler.ListDataHandler(
                data, historical_context_number
            )
        elif data and inspect.isgenerator(data)or hasattr(data, "__next__"):
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
            context, update =  self.data_handler.next()
        except NoMoreData:
            raise StopIteration
        return context, update

    def _push_update(self, context, update):
        d = {
            "context": [candle.to_dict() for candle in context],
            "update": update.to_dict()
        }


    def _dry_push_update(self, context, update):
        return core.const.Signal.NO_ACTION
