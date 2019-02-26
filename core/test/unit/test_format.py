import datetime as dt
import core

def test_candle_serialisation():
    open, low, high, close, volume = 100, 90, 110, 105, 112344
    this_dt = dt.datetime(year=2018, month=1, day=1)
    candle = core.format.Candle(this_dt, "", open, high, low, close, volume)
    candle = candle.to_dict()
    candle = core.format.Candle.from_dict(candle)

    assert candle.datetime == this_dt
    assert candle.low == low
    assert candle.high == high
    assert candle.close == close
    assert candle.open == open
    assert candle.volume == volume
