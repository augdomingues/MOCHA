from ConfigurationParameters import ConfigurationParameters
from Parser import Parser
from Extractor import Extractor
from Classifier import Classifier
import sys
import os
from Bar import Bar
import Extractor2_0

class Principal:

    def __init__(self):
        self.metrics = []
        self.blocking = []
        self.readConfigurationParameters()
        self.summary = {"-ps": "Parsing SWIM ", "-e": "Extracting ",
                        "-pr": "Parsing RAW ", "-c":  "Classify metrics ",
                        "-id": "Report users' ID "}

    def usage(self):
        print("+-----------------------------------------------------------+")
        print("|                                                           |")
        print("|    ( (                                                    |")
        print("|   _)_)_                                                   |")
        print("| c(  M  ) MOCHA: tool for MObility CHaracteristics Analysis|")
        print("| ,-\___/-.                                                 |")
        print("| `-------'                                                 |")
        print("|                                                           |")
        print("| Usage: Principal.py [-pr, -ps, -e, -c, -id] filename      |")
        print("|                                                           |")
        print("| ['-pr', '-ps', '-e']: Parse (RAW), Parse (SWIM) , Extract |")
        print("| [ '-c' ]      : Classify distributions                    |")
        print("| [ '-id']      : Report ID                                 |")
        print("| filename      : file to be parsed/processed               |")
        print("|               FILENAME MUST BE THE LAST ARGUMENT          |")
        print("+-----------------------------------------------------------+")

    def validate_input(self, args):
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
        print("\n\t\t\t", end="")
        for i in range(0, len(args) - 1):
            print(self.summary[args[i]], end="")
        print("from {}\n".format(args[-1]))

    def parse(self, parser, args):
        filename = ""
        if "-pr" in args:
            filename = parser.parseRaw(args[-1])
        elif "-ps" in args:
            filename = parser.parseSwim(args[-1])
        return filename

    def extract(self, parser, extractor, args, filename):
        if "-e" in args:
            self.readMetrics()
            # If the flag to parse is not provided,
            # then the parsed file is the one passed as input
            if "-pr" not in args and "-ps" not in args:
                filename = args[-1]
                parser.collectMaxes(filename)
                fsize = parser.filesize
            else:
                fsize = parser.parsedfilesize/2
            radius = self.configurationParameters.communicationRadius
            #extractor = Extractor(filename, parser.maxT, parser.maxX,
            #                       parser.maxY, radius, fsize,
            #                       self.metrics, "-id" in args)

            m, b = self.metrics, self.blocking

            extractor = Extractor2_0.Extractor(filename, m, "-id" in args, b)
            extractor.extract()
        return filename

    def classify(self, args, filename):
        # If user is running only the classifying module
        if filename == "":
            filename = args[-1]
        if "-c" in args:
            classifier = Classifier(filename)
            classifier.classify()

    def main(self, args):
        self.readConfigurationParameters()
        parser = None
        extractor = None
        if self.validate_input(args):
            self.summarize(args)
            # Parse trace
            parser = Parser(self.configurationParameters.communicationRadius)
            filename = self.parse(parser, args)

            # Extract characteristics
            filename = self.extract(parser, extractor, args, filename)

            # Classify characteristics
            self.classify(args, filename)

    def readMetrics(self):
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

    def readConfigurationParameters(self):
        # TODO ler outro parametro do arquivo de configuracao
        if os.path.exists("config.txt"):
            with open("config.txt", "r") as entrada:
                self.configurationParameters = ConfigurationParameters()
                line = entrada.readline()
                line = line.split(" ")
                radius = float(line[1])
                self.configurationParameters.communicationRadius = radius
        else:
            print("Configuration file not found! Recreating!")
            cp = ConfigurationParameters()
            cp.recreateConfigurationFile()



if __name__ == "__main__":
    a = Principal()
    a.main(sys.argv[1:])
