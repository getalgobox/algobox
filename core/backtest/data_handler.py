import abc
import collections

from abc import ABC, abstractmethod

from core.exceptions import NoMoreData

class DataHandler(ABC):
    """
    DataHandlers will standardise the interface for backtesting for different
    types of sources. The user may provide a list of data, they may provide a
    generator, a file or something else.

    This interface makes it simple to add more supported types to the Backtesting
    engine and makes it pretty easy to implement a type.

    What should the behaviour be when we have no further data? !TODO
    """

    @abstractmethod
    def _get_context(*args, **kwargs):
        raise NotImplementedError("This method must be implemented in the child")

    @abstractmethod
    def _get_update(*args, **kwargs):
        raise NotImplementedError("This method must be implemented in the child")

    def next(self):
        """
        Users should use this method for accessing data, to ensure the correct
        order is used. For example, calling update before context would add
        the update to the context.. not ideal.
        """
        context = self._get_context()
        update = self._get_update()
        return context, update

class ListHandler(DataHandler):
    def __init__(self, list, historical_context_number):
        self.data = list
        self.context = collections.deque(maxlen=5)
        self.historical_context_number = historical_context_number
        self.index = self.historical_context_number


    def _get_context(self):
        context_slice = slice(self.index - self.historical_context_number,self.index)
        return self.data[context_slice]


    def _get_update(self):
        try:
            update = self.data[self.index]
        except IndexError:
            raise NoMoreData("We have no more data available for this series")
        
        self.index += 1
        return update



class GeneratorHandler(DataHandler):
    def __init__(self, generator, historical_context_number):
        self.generator = generator
        self.historical_context_number = historical_context_number
        self.context = collections.deque(maxlen=historical_context_number)
        self._init_context()

        self.last_update = None

    def _init_context(self):
        """
        Generators produce updates one at a time, however - we need to have
        some historical context to perform time series analyis on. This
        is specified by the `historical_context_number` parameter. An algorithm
        cannot begin analysis without this context.
        """
        for _ in range(0, self.historical_context_number):
            self.context.append(next(self.generator))

    def _get_context(self):
        return list(self.context)

    def _get_update(self):
        try:
            update = next(self.generator)
        except StopIteration:
            raise NoMoreData("We have no more data available for this series")

        self.context.append(update)
        return update

class CSVGeneratorHandler(DataHandler):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("This class is not yet implemented. \
        Process the csv yourself either into a list of core.format.Candle's \
        or a generator producing the same.")
