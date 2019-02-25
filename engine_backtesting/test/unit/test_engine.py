import os
import json
import random
import uuid

import datetime as dt

import pytest

from backtest.engine import Backtest
import core

@pytest.fixture
def daily_series():
    dt_from = dt.datetime(year=2018, month=10, day=1)
    dt_to = dt.datetime(year=2019, month=2, day=1)

    data = core.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt_from,
        dt_to=dt_to,
        trading_hours=self.core.time.FTSE(),
        interval="1d",
        topic="GDAX:BTC-USD:5M"
    )

    return data

def test_run_backtest(daily_series):
    dt_from = dt.datetime(year=2018, month=10, day=1)
    dt_to = dt.datetime(year=2019, month=2, day=1)

    data = core.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt_from,
        dt_to=dt_to,
        trading_hours=self.core.time.FTSE(),
        interval="1d"
    )

    bt = Backtest("GDAX:BTC-USD:5M", )

def test_no_look_forward(daily_series):
    for day in daily_series:
        pass
