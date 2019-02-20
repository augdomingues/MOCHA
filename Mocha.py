"""
    This module contains the main class that executes the MOCHA framework.
"""
import sys
from ConfigurationParameters import ConfigurationParameters
from Parser import Parser
from Classifier import Classifier
from extractor import Extractor


class Principal:
    """ Main class for the MOCHA project. """

    def __init__(self):
        """ Initiate class structures. """
        self.metrics = []
        self.blocking = []
        self.read_configuration_parameters()
        self.summary = {"-ps": "Parsing SWIM ",
                        "-e": "Extracting ",
                        "-pr": "Parsing RAW ",
                        "-c":  "Classify metrics ",
                        "-id": "Report users' ID "}

    def usage(self):
        """ Visual guidance of how to use MOCHA. """
        print("+-----------------------------------------------------------+")
        print("|                                                           |")
        print("|    ( (                                                    |")
        print("|   _)_)_                                                   |")
        print("| c(  M  ) MOCHA: tool for MObility CHaracteristics Analysis|")
        print("| ,-\___/-.                                                 |") # noqa
        print("| `-------'                                                 |")
        print("|                                                           |")
        print("| Usage: Mocha.py [-pr, -ps, -e, -c, -id] filename          |")
        print("|                                                           |")
        print("| ['-pr', '-ps', '-e']: Parse (RAW), Parse (SWIM) , Extract |")
        print("| [ '-c' ]      : Classify distributions                    |")
        print("| [ '-id']      : Report ID                                 |")
        print("| filename      : file to be parsed/processed               |")
        print("|               FILENAME MUST BE THE LAST ARGUMENT          |")
        print("+-----------------------------------------------------------+")

    def validate_input(self, args):
        """ Checks if the input parameters are valid. """
        valid_args = ["-ps", "-e", "-pr", "-c", "-id"]
        for i in range(0, len(args)-1):
            if "-" in args[i] and args[i] not in valid_args:
                self.usage()
                return False
        if "-help" in args or len(args) < 2:
            self.usage()
            return False
        return True

    def summarize(self, args):
        """ Output the selected steps. """
        print("\n\t\t\t", end="")
        for i in range(0, len(args) - 1):
            print(self.summary[args[i]], end="")
        print("from {}\n".format(args[-1]))

    def parse(self, args):
        """ Parse the input trace file. """

        parser = Parser(ConfigurationParameters.communicationRadius)
        filename = ""
        if "-pr" in args:
            filename = parser.naive_raw(args[-1])
        elif "-ps" in args:
            filename = parser.parse_swim(args[-1])
        return filename

    def validate_trace(self, filename):
        """ Validates the parsed trace before processing it. """
        with open(filename, "r") as inn:
            for index, line in enumerate(inn):
                if len(line.strip().split()) < 9:
                    print("Invalid input trace error:")
                    print("Line {} has less than 9 fields".format(index))
                    raise

    def extract(self, args, filename):
        """ Extracts the metrics from the parsed file. """
        self.read_metrics()
        has_id = "-id" in args
        Extractor(filename, self.metrics,
                  has_id, self.blocking).extract()

    def classify(self, args, filename):
        """ Classify the metrics by their statistical distributions. """

        # If user is running only the classifying module
        if filename == "":
            filename = args[-1]
        if "-c" in args:
            Classifier(filename).classify()

    def main(self, args):
        """ Main method that calls each step."""
        filename = args[-1]

        if self.validate_input(args):
            self.summarize(args)
            # Parse trace
            if "-pr" in args or "-ps" in args:
                filename = self.parse(args)

            # Extract characteristics
            if "-e" in args:
                self.validate_trace(filename)
                self.extract(args, filename)

            # Classify characteristics
            if "-c" in args:
                self.classify(args, filename)

    def read_metrics(self):
        """ Read metrics from the metric selection file. """
        with open("metrics.txt", "r") as entrada:
            for line in entrada:
                line = line.strip().replace(" ", "")
                if line[0] == "#":
                    continue
                if line[-1] == "*":
                    line = line[0:-1]
                    self.blocking.append(line)
                else:
                    self.metrics.append(line)

    def read_configuration_parameters(self):
        """ Read the config parameters from the file. If not exist, create. """
        ConfigurationParameters()


if __name__ == "__main__":
    MOCHA = Principal()
    MOCHA.main(sys.argv[1:])
