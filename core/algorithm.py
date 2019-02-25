from abc import ABC
from abc import abstractmethod

class ABAlgorithm(ABC):

    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def on_data(self):
        pass
