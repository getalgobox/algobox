import random

import datetime as dt

import pytest

from core.time import FTSE
from core.time import interval_string_to_time_delta

def test_trading_hours_open_at():
    assert FTSE().open_at(
        dt.datetime(
            year=2019, month=2, day=20,
            hour=9, minute=5
        )
    )

    assert FTSE().open_at(
        dt.datetime(
            year=2019, month=2, day=20,
            hour=16, minute=59
        )
    )

    assert not FTSE().open_at(
        dt.datetime(
            year=2019, month=2, day=23,
            hour=16, minute=59
        )
    )

    assert not FTSE().open_at(
            dt.datetime(
                year=2019, month=2, day=28,
                hour=19, minute=59
            )
        )

def test_trading_hours_next_open():
    # check that on friday at 9:30 AM the next open is the following
    # monday at 9:00 AM
    assert FTSE().next_open(
        dt.datetime(
            year=2019, month=2, day=22,
            hour=9, minute=30
        )
    ) == dt.datetime(year=2019, month=2, day=25,
        hour=9, minute=0
    )

    # check that on Saturday the net open is Monday
    assert FTSE().next_open(
        dt.datetime(
            year=2019, month=2, day=23,
            hour=12, minute=30
        )
    ) == dt.datetime(year=2019, month=2, day=25,
        hour=9, minute=0
    )

def test_next_open_same_day_bug():
    """
    This bug meant that if we were before open and checked for next open,
    we skipped todays open and moved right to tomorrows. This is undesired
    behaviour for the next_open method, as if the current time isn't open
    then the next_open should be today if today is a trading day.
    """

    assert FTSE().next_open(
        dt.datetime(
            year=2019, month=2, day=18,
            hour=1, minute=12
        )
    ) == dt.datetime(year=2019, month=2, day=18,
        hour=9, minute=0
    )

    assert FTSE().next_open(
        dt.datetime(
            year=2019, month=2, day=22,
            hour=6, minute=12
        )
    ) == dt.datetime(year=2019, month=2, day=22,
        hour=9, minute=0
    )



def test_candle_string_to_time_delta():
    assert interval_string_to_time_delta("30s") == dt.timedelta(seconds=30)

    assert interval_string_to_time_delta("3m") == dt.timedelta(minutes=3)
    assert interval_string_to_time_delta("5m") == dt.timedelta(minutes=5)

    assert interval_string_to_time_delta("10h") == dt.timedelta(hours=10)
    assert interval_string_to_time_delta("8h") == dt.timedelta(hours=8)
    assert interval_string_to_time_delta("3h") == dt.timedelta(hours=3)

    assert interval_string_to_time_delta("3d") == dt.timedelta(days=3)
    assert interval_string_to_time_delta("10d") == dt.timedelta(days=10)
