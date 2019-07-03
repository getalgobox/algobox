import pytest
import datetime as dt

import core

from core.backtest import data_handler
from core.exceptions import NoMoreData

def timeseries():
    gen = core.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt.datetime(year=2018, month=1, day=1, hour=9),
        dt_to=dt.datetime(year=2018, month=1, day=31, hour=9),
        trading_hours=core.time.FTSE(),
        interval="1d",
        topic="FTSE:LLOY:1D"
    )
    return gen

LOOKBACK_PERIOD = 7

@pytest.mark.parametrize("timeseries,handler",
    [
        (timeseries(), data_handler.GeneratorHandler),
        (list(timeseries()), data_handler.ListHandler),
    ]
)
def test_data_handlers(timeseries, handler):
    """
    We expect the handlers to react in the same way according to the DataHandler
    interface.
    """
    handler = handler(timeseries, LOOKBACK_PERIOD)
    updates = []
    i = 0
    while True:
        try:
            context, update = handler.next()
            i += 1
            assert len(context) == LOOKBACK_PERIOD
        except NoMoreData:
            break

        updates.append(update)
        assert context[-1].datetime < update.datetime

    # total lenght of series(23) - context(7) which aren't provided as updates
    assert i == 16
    updates = [x.datetime.date().isoformat() for x in updates]
    assert updates[10] == "2018-01-24"
