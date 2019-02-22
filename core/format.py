import datetime as dt

class DataFormat(object):
    pass

class Candle(DataFormat):
    def __init__(self, d):
        self.datetime = None # !TODO
        self.open = d["open"]
        self.low = d["low"]
        self.high = d["high"]
        self.close = d["close"]

        if "volume" in d:
            self.volume = d["volume"]
        else:
            self.volume = None

        self.data = d

    @property
    def price(self):
        return self.close

    @property
    def average_price(self):
        # exclude volume
        return sum(self.open, self.low, self.high, self.close) / 4




class Tick(DataFormat):
    pass
