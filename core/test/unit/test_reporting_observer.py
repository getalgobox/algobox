import uuid

import pytest

import datetime as dt

import core

from core.reporting.observer import ABObserver
from core.event import ABEvent


@pytest.fixture
def clean_observer():
    return ABObserver()

@pytest.fixture
def complete_bt():
    dt_from = dt.datetime(year=2015, month=1, day=1)
    dt_to = dt.datetime(year=2018, month=12, day=1)

    daily_series = core.ts_generator.CandleTimeSeriesGenerator(
        dt_from=dt_from,
        dt_to=dt_to,
        trading_hours=core.time.FTSE(),
        interval="1d",
        topic="GDAX:BTC-USD:1D"
    )

    bt = core.backtest.manager.BacktestManager(
        topic="GDAX:BTC-USD:1D",
        dt_from=daily_series.start,
        dt_to=daily_series.end,
        algo_id=str(uuid.uuid4()),
        historical_context_number=30,
        data=daily_series
    )

    bt.push_update = bt._dry_push_random_signal

    for context, update in bt:
        pass

    return bt

# def test_observer(complete_bt):
#     bt = complete_bt
#     observer = complete_bt.observer
