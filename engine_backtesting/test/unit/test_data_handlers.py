import pytest
import datetime as dt

import core

from backtest import test_data_hadlers

def timeseries():
    gen = backtest.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt.datetime(year=2018, month=1, day=1, hour=9),
        dt_from=dt.datetime(year=2018, month=2, day=1, hour=9),
        trading_hours=core.time.FTSE(),
        interval="1d",
        topic="FTSE:LLOY:1D"
    )
    return gen


@pytest.mark.parametrize("timeseries,handler",
    [
        (list(timeseries()), test_data_hadlers.ListHandler),
        (timeseries(), test_data_hadlers.GeneratorHandler)
    ]
)
def test_data_handlers(timeseries, handler):
    """
    We expect the handlers to react in the same way according to the DataHandler
    interface. so there is no need for seperate tests.
    """
    handler(timeseries)
    context, update = handler.next()
