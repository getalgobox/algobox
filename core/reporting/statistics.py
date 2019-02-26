from abc import ABC, abstractmethod

class ABStatistic(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def compute(self, series):
        raise NotImplementedError("Implement this method in child class.")

class MaxDrawDown(ABStatistic):
    pass

class AvgHoldTime(ABStatistic):
    pass

class TradesPerDay(ABStatistic):
    pass

class SharpeRatio(ABStatistic):
    pass

class RoI(ABStatistic):
    pass

class RoIVsMarket(ABStatistic):
    pass
