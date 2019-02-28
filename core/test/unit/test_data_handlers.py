import pytest
import datetime as dt

import core

from core.backtest import data_handler
from core.exceptions import NoMoreData

def timeseries():
    gen = core.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt.datetime(year=2018, month=1, day=1, hour=9),
        dt_to=dt.datetime(year=2018, month=2, day=1, hour=9),
        trading_hours=core.time.FTSE(),
        interval="1d",
        topic="FTSE:LLOY:1D"
    )
    return gen

LOOKBACK_PERIOD = 5

@pytest.mark.parametrize("timeseries,handler",
    [
        (timeseries(), data_handler.GeneratorHandler),
        (list(timeseries()), data_handler.ListHandler),
    ]
)
def test_data_handlers(timeseries, handler):
    """
    We expect the handlers to react in the same way according to the DataHandler
    interface. so there is no need for seperate tests.
    """
    handler = handler(timeseries, LOOKBACK_PERIOD)
    updates = []
    i = 0
    while True:
        try:
            context, update = handler.next()
        except NoMoreData:
            break
        i += 1

        updates.append(update)
        assert context[-1].datetime < update.datetime

    # total lenght of series(25) - context(5) which aren't provided as updates
    assert i == 20
    updates = [x.datetime.date().isoformat() for x in updates]
    assert updates[10] == "2018-01-22"
