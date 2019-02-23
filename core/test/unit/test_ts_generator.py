import random

import datetime as dt

import pytest

from core.ts_generator import CandleTimeSeriesGenerator
from core.time import FTSE

@pytest.fixture()
def candles():
    dt_from = dt.datetime(year=2018, month=1, day=1)
    dt_to = dt.datetime(year=2019, month=1, day=1)
    gen = CandleTimeSeriesGenerator(dt_from, dt_to, FTSE(), "1h")
    candles = list(gen)
    return candles

# pytest offers something better than looped asserts but it's 6:03AM.. zzz
def test_close_open_consistency(candles):
    for i, candle in enumerate(candles[0:-2]):
        assert candles[i].close == candles[i+1].open
