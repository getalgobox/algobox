class ABObserver(object):
    """
    Observes statistics
    """
    def __init__(self):
        self.equity_series = []
        self.event_series = []

    def observe_event(self, event):
        self.event_series.append(event)

    def observe_equity(self, event):
        self.equity.series.append(event)
