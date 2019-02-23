
class Backtest(object):

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
        :param data: optional list of ABDataFormat instances, candle or tick.
         Currently, we are only supporting candles. If this list is not provided
         data will be queried from the TSDB (tbd).
        """

        self.data = data

        if not data:
            # query all data
            pass

        self.data = [core.format.Candle(d) for d in data]

    def _finalise_backtest(self):
        """
        This method will update the backtest record with the final results.
        """
        pass

    def next(self):
        """
        Give the next update.
        """
        pass

    def main(self):
        for i, update in enumerate(self.data[historical_context_number:-1]):
            context = {
                "update": update,
                "context": self.data[i:i+]
                "format": self.format
                "topic": self.topic
            }
