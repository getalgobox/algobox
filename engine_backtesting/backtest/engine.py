
class Backtest(object):

    def __init__(self, topic, from, to, algo_id, historical_context_number=30,
        data=None, format="CANDLE"
        ):
        """
        The backtest instance. This is the class that will drive the backtest.

        It knows only the id of the algorithm it will call, nothing about the
        code it will execute.
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
        for update in self.data[historical_context_number:-1]:
            context = {
                "update": update
            }
