# the purpose of these generators are to serve in place as real data
# for the purposes of testing and development while the data sources
# are not implemented

import uuid
import random

import datetime as dt

import numpy as np

import core.time
import core.format


class CandleTimeSeriesGenerator(object):
    def __init__(self, dt_from, dt_to, trading_hours, interval):
        """
        Random candle series. Not appropriate for testing strategies, only
        for testing the application itself.

        !TODO refactor to reduce reuse

        :param dt_from: datetime; when to start
        :param dt_to: datetime; when to finish
        :param trading_hours: core.time.TradingHours; a TradingHours child class
         describing trading hours for the exchange of this thing.
        :interval integer:
        """

        self.start = dt_from
        self.end = dt_to

        # str is now equivalent to basestring for str type checking in py3?
        if isinstance(interval, str):
            interval = core.time.interval_string_to_time_delta(interval)
        self.interval = interval

        self.previous_candle = None
        self.trading_hours = trading_hours

    def __iter__(self):
        stdev = 0.03
        this_dt = self.start

        while this_dt <= self.end:
            if not self.previous_candle:
                if self.trading_hours.open_at(self.start):
                    this_dt = self.start
                else:
                    this_dt = self.trading_hours.next_open(self.start)

                mean = random.randint(20, 250)
                random_prices = list(np.random.normal(loc=mean, scale=stdev, size=64))
                random_prices = sorted({round(p, 2) for p in random_prices})

                # we could ensure open and close are unique, but that wouldn't
                # be elegant and sometimes they are the same irl.
                new_candle = core.format.Candle(
                    this_dt=this_dt,
                    high=random_prices[-1],
                    low=random_prices[0],
                    open=random.choice(random_prices[1:-2]),
                    close=random.choice(random_prices[1:-2]),
                    volume=random.randint(1000, 100000)
                )
                self.previous_candle = new_candle

                yield new_candle

            this_dt = self.previous_candle.this_dt + self.interval
            if not self.trading_hours.open_at(this_dt):
                this_dt = self.trading_hours.next_open(this_dt)

            mean = self.previous_candle.close
            random_prices = list(np.random.normal(loc=mean, scale=stdev, size=64))
            random_prices = sorted({round(p, 2) for p in random_prices})

            new_candle = core.format.Candle(
                this_dt=this_dt,
                high=random_prices[-1],
                low=random_prices[0],
                open=self.previous_candle.close,
                close=random.choice(random_prices[1:-2]),
                volume=random.randint(1000, 100000)
            )
            self.previous_candle = new_candle

            yield new_candle
        # StopIteration is depreciated. Just use return.
        return
