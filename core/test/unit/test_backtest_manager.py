import os
import json
import random
import uuid

import datetime as dt

import pytest

import core
from core.backtest.manager import BacktestManager

@pytest.fixture
def daily_series():
    dt_from = dt.datetime(year=2015, month=1, day=1)
    dt_to = dt.datetime(year=2018, month=12, day=1)

    data = core.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt_from,
        dt_to=dt_to,
        trading_hours=core.time.FTSE(),
        interval="1d",
        topic="GDAX:BTC-USD:1D"
    )

    return data

def test_run_backtest(daily_series):

    bt = BacktestManager(
        topic="GDAX:BTC-USD:1D",
        dt_from=daily_series.start,
        dt_to=daily_series.end,
        algo_id=str(uuid.uuid4()),
        lookback_period=30,
        data=daily_series
    )

    bt.push_update = bt._dry_push_update

    prev_update = None

    for context, update in bt:
        if prev_update:
            assert context[-1] == prev_update
            assert len(context) == 30
            assert max(context) < update
