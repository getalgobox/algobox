import datetime as dt

class ABDataFormat(object):
    pass

class Candle(ABDataFormat):
    def __init__(self, this_dt, open, high, low, close, volume=None):
        self.this_dt = this_dt
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    @property
    def price(self):
        return self.close

    @property
    def average_price(self):
        # exclude volume
        return sum(self.open, self.high, self.low, self.close) / 4

    def __repr__(self):
        return "<algobox.core.format.Candle> {}|O:{}|H:{}|L:{}|C:{}|V:{}".format(
            self.this_dt.isoformat(), self.open, self.high, self.low, self.close, self.volume
        )


    @classmethod
    def from_dict(cls, d):
        volume = d.get("volume", None)
        return cls(
            this_dt=d["this_dt"],
            open=d["open"],
            low=d["low"],
            high=d["high"],
            close=d["close"],
            volume=volume
        )

    def to_dict(self):
        return {
            "this_dt": self.this_dt,
            "open": self.open,
            "low": self.low,
            "high": self.high,
            "close": self.close,
            "volume": self.volume
        }

class Tick(ABDataFormat):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("the Tick data format is not currently supported")
