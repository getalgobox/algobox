import datetime as dt

import core.exceptions

"""
The TradingHours classes are very basic for now. We will need something more
comprehensive. For example; bank holidays, christmas, thanksgiving etc
"""

class TradingHours(object):
    pass

    def open_at(self, this_dt):
        if this_dt.time() >= self.open and this_dt.time() <= self.close \
        and this_dt.isoweekday() in self.trading_days:
            return True
        else:
            return False

    def next_open(self, this_dt):
        """
        Provides the open time of the next trading session. If current dt is
        open, we provide the next trading open.

        For example if we ask for the next open at 1PM on a Friday, we'll return
        9AM on Monday [FTSE].

        If the current dt is at 1AM on monday we should return 9AM that same
        monday.
        """

        if this_dt.isoweekday() in self.trading_days and this_dt.time() < self.open:
            return dt.datetime.combine(this_dt.date(), self.open)

        for i in range(1, 8):
            days_td = dt.timedelta(days=i)
            temp_dt = this_dt + days_td
            if temp_dt.isoweekday() in self.trading_days:
                # combine the next open date with the open time from the class
                return dt.datetime.combine(this_dt.date() + days_td, self.open)
        raise core.exceptions.ABBaseException("Unable to find next open")

class FTSE(TradingHours):
    open = dt.time(hour=9, minute=0)
    close = dt.time(hour=17, minute=0)
    trading_days = {1, 2, 3, 4, 5}
    tz = None


class CryptoGeneral(TradingHours):
    open = dt.time(hour=0, minute=0)
    close = dt.time(hour=23, minute=59, second=59, microsecond=999999)
    trading_days = {1, 2, 3, 4, 5, 6, 7}
    tz = None

def interval_string_to_time_delta(interval):
    """
    Probably whatever datastore solution we choose will support strings like
    '5m' etc, but for generating series for tests and dev this will be needed.
    """

    unit_timedelta_map = {
        "s": dt.timedelta(seconds=1),
        "m": dt.timedelta(minutes=1),
        "h": dt.timedelta(hours=1),
        "d": dt.timedelta(days=1)
    }

    interval = interval.lower()

    time_unit = interval[-1]
    time_quantity = interval[0:-1]

    interval_secs = int(time_quantity) * unit_timedelta_map[time_unit].total_seconds()
    this_td = dt.timedelta(seconds=interval_secs)

    return this_td
