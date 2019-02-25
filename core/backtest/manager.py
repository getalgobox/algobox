import inspect

class BacktestManager(object):

    def __init__(self, topic, dt_from, dt_to, algo_id, historical_context_number=30,
        data=None):
        """
        The backtest instance. This is the class that will drive the backtest.

        It knows only the id of the algorithm it will call, nothing about the
        code it will execute.

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

        if data and isinstance(data, list):
            self.list_handler = ListDataHandler(data, historical_context_number)
        elif data and inspect.isgenerator(data):
            self.data_handler = GeneratorHandler(data, historical_context_number)
        else:
            raise NotImplemented("No data was provided, we do not currently \
            support retrieving this from a database. Please provide the `data` \
            parameter. See docs/help.")

        def temp_push_to_algo(*args, **kwargs):
            """
            In reality we want to push to the algoservice as if we were the
            data service, but for now we can pretend that we received a
            `core.Signal.NO_ACTION` in response.
            """
            return const.Signal.NO_ACTION

        self.push_to_algo = temp_push_to_algo
