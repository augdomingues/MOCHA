from abc import abstractmethod, ABCMeta
from time import time


class Metric(metaclass=ABCMeta):
    """ An abstract class that represents a metric in MOCHA. """

    Metrics = {}

    @abstractmethod
    def __init__(self, name, *args, **kwargs):
        pass

    @abstractmethod
    def print(self, *args, **kwargs):
        """ Prints the metric to the output file. """
        pass

    @abstractmethod
    def extract(self, *args, **kwargs):
        """ Performs the extraction of the metric. """
        pass

    @abstractmethod
    def explain(self, *args, **kwargs):
        """ Provides a str that describes the metric. """
        pass

    @abstractmethod
    def commit(self, *args, **kwargs):
        """ Returns the shared data between metrics """
        pass

    def timeexecution(func):
        """ Measures the execution time of a function. """
        def wrapper(*args, **kwargs):

            # Extract time diff
            begin = time()
            func(*args, **kwargs)
            end = time()
            diff = end - begin
            diff = round(diff, 2)

            # Get function name
            classname = args[0].__class__.__name__
            funcname = func.__name__
            name = "{}.{}".format(classname, funcname)

            print("{} took {} seconds".format(name, diff))
        return wrapper


