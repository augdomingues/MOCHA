"""
    This module contains the main class that executes the MOCHA framework.
"""
import sys
import os
from ConfigurationParameters import ConfigurationParameters
from Parser import Parser
from Classifier import Classifier
import Extractor2_0

class Principal:

    def __init__(self):
        """ Initiate class structures. """
        self.metrics = []
        self.blocking = []
        self.read_configuration_parameters()
        self.summary = {"-ps": "Parsing SWIM ", "-e": "Extracting ",
                        "-pr": "Parsing RAW ", "-c":  "Classify metrics ",
                        "-id": "Report users' ID "}

    def usage(self):
        """ Visual guidance of how to use MOCHA. """
        print("+-----------------------------------------------------------+")
        print("|                                                           |")
        print("|    ( (                                                    |")
        print("|   _)_)_                                                   |")
        print("| c(  M  ) MOCHA: tool for MObility CHaracteristics Analysis|")
        print("| ,-\___/-.                                                 |")
        print("| `-------'                                                 |")
        print("|                                                           |")
        print("| Usage: Mocha.py [-pr, -ps, -e, -c, -id] filename      |")
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
        if "-help" in args:
            self.usage()
            return False
        if len(args) < 2:
            self.usage()
            return False
        return True

    def summarize(self, args):
        """ Output the selected steps. """
        print("\n\t\t\t", end="")
        for i in range(0, len(args) - 1):
            print(self.summary[args[i]], end="")
        print("from {}\n".format(args[-1]))

    def parse(self, parser, args):
        """ Parse the input trace file. """
        filename = ""
        if "-pr" in args:
            filename = parser.naive_raw(args[-1])
        elif "-ps" in args:
            filename = parser.parse_swim(args[-1])
        return filename

    def extract(self, extractor, args, filename):
        """ Extracts the metrics from the parsed file. """
        if "-e" in args:
            self.read_metrics()
            metrics, blocking = self.metrics, self.blocking
            has_id = "-id" in args
            extractor = Extractor2_0.Extractor(filename, metrics, has_id, blocking)
            extractor.extract()
        return filename

    def classify(self, args, filename):
        """ Classify the metrics by their statistical distributions. """
        # If user is running only the classifying module
        if filename == "":
            filename = args[-1]
        if "-c" in args:
            classifier = Classifier(filename)
            classifier.classify()

    def main(self, args):
        """ Main method that calls each step."""
        self.read_configuration_parameters()
        parser = None
        extractor = None
        if self.validate_input(args):
            self.summarize(args)
            # Parse trace
            parser = Parser(self.configurationParameters.communicationRadius)
            filename = self.parse(parser, args)

            # Extract characteristics
            filename = self.extract(extractor, args, filename)

            # Classify characteristics
            self.classify(args, filename)

    def read_metrics(self):
        """ Read metrics from the metric selection file. """
        head = "INCO\nCODU\nSOCOR\nEDGEP\nTOPO\nRADG\nVIST\nTRVD\nSPAV\nCONEN"
        if not os.path.exists("metrics.txt"):
            with open("metrics.txt", "w+") as entrada:
                entrada.write("# Use a # to ignore a metric\n")
                entrada.write(head)

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
        """ Read the config parameters from the file. If it not exist, create it. """
        if os.path.exists("config.txt"):
            with open("config.txt", "r") as entrada:
                self.configurationParameters = ConfigurationParameters()
                line = entrada.readline()
                line = line.split(" ")
                radius = float(line[1])
                self.configurationParameters.communicationRadius = radius * 1000
                print("Radius is: {}".format(radius))
        else:
            print("Configuration file not found! Recreating!")
            config_parameters = ConfigurationParameters()
            config_parameters.recreateConfigurationFile()



if __name__ == "__main__":
    MOCHA = Principal()
    MOCHA.main(sys.argv[1:])
