import core

class Topic(object):
    def __init__(self, topic):
        """
        A topic looks like this `IG:LLOY:5M` and contains three peices of data.

        1) The exchange the asset is trading on
        2) The asset being traded
        3) The frequency of the updates to this data

        This class creates properties and conveniences for topics represented
        in this way.
        """
        x = topic.split(":")
        self.exchange = x[0]
        self.asset = x[1]
        self.interval = x[2]
        self.interval_timedelta = core.time.interval_string_to_time_delta(
            self.interval
        )
        self.raw = topic

    def __repr__(self):
        return self.raw
