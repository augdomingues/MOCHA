from abc import abstractmethod, ABCMeta
from time import time


"""

    An abstract class that represents a metric in MOCHA

"""
class Metric(metaclass=ABCMeta):

    Metrics = {}

    @abstractmethod
    def __init__(self, name, *args, **kwargs):
        pass

    @abstractmethod
    def print(self, *args, **kwargs):
        pass

    @abstractmethod
    def extract(self, *args, **kwargs):
        pass

    @abstractmethod
    def explain(self, *args, **kwargs):
        pass

    @abstractmethod
    def commit(self, *args, **kwargs):
        pass

    def timeexecution(func):
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


