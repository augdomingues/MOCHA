from ConfigurationParameters import ConfigurationParameters
from Parser import Parser
from Extractor import Extractor
from Classifier import Classifier
import sys
import os
from Bar import Bar

class Principal:
 
    def __init__(self):
        self.metrics = {}
        self.readConfigurationParameters()
        self.summary = {"-ps": "Parsing SWIM ", "-e": "Extracting ", "-pr": "Parsing RAW ", "-c":  "Classify metrics ", "-id": "Report users' ID "}

    def usage(self):
        print("+--------------------------------------------------------------------------+")
        print("|                                                                          |")
        print("|    ( (                                                                   |")
        print("|    _)_)_                                                                 |")
        print("|  c(  M  )     MOCHA: a tool for MObility CHaracteristics Analysis        |")
        print("|  ,-\___/-.                                                               |")
        print("|  `-------'                                                               |")
        print("|                                                                          |")
        print("| Usage: Principal.py ['-pr', '-ps', '-e', '-c', '-id']  filename          |")
        print("|                                                                          |")
        print("| ['-pr', '-ps', '-e']: Parse (RAW), Parse (SWIM) , Extract                |")
        print("| [ '-c' ]      : Classify distributions                                   |")
        print("| [ '-id']      : Report ID ( not to be used with '-c')                    |")
        print("| filename        : file to be parsed/processed                            |")
        print("|               FILENAME MUST BE THE LAST ARGUMENT                         |")
        print("+--------------------------------------------------------------------------+")
    
    def validate_input(self,args):
        for i in range(0,len(args)-1):
            if "-" in args[i] and args[i] not in ["-ps", "-e", "-pr", "-c", "-id"]:
                self.usage()
                return False
        if "-help" in args:
            self.usage()
            return False
        if len(args) < 2:
            self.usage()
            return False
        return True

    def summarize(self,args):
        print("\n\t\t\t",end="")
        for i in range(0,len(args) - 1):
            print(self.summary[args[i]],end="")
        print("from {}\n".format(args[-1]))

    def parse(self,parser,args):
        filename = ""
        if "-pr" in args:
            filename = parser.parseRaw(args[-1])
        elif "-ps" in args:
            filename = parser.parseSwim(args[-1])
        return filename


    def extract(self,parser,extractor,args,filename):

        if "-e" in args:
            self.readMetrics()
            # If the flag to parse is not provided, then the parsed file is the one passed as input
            if "-pr" not in args and "-ps" not in args:
                filename = args[-1]
                parser.collectMaxes(filename)
                filesize = parser.filesize
            else:
                filesize = parser.parsedfilesize/2
                                                                                                                                        # Checks to report ID or not
            extractor = Extractor(filename,parser.maxT,parser.maxX,parser.maxY,self.configurationParameters.communicationRadius,filesize,self.metrics, "-id" in args)
            extractor.extract()

        return filename

    def classify(self,args,filename):
        # If user is running only the classifying module
        if filename == "":
            filename = args[-1]
        if "-c" in args:
            if "-id" in args:
                print("Can't classify with User IDs. Abborting classification...")
                return
            else:
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
            filename = self.parse(parser,args)

            # Extract characteristics
            filename = self.extract(parser,extractor,args,filename)

            # Classify characteristics
            self.classify(args,filename)

    def readMetrics(self):
        if not os.path.exists("metrics.data"):
            with open("metrics.data", "w+") as entrada:
                entrada.write("# Use a # to ignore a metric\n")
                entrada.write("INCO\nCODU\nSOCOR\nEDGEP\nTOPO\nRADG\nVIST\nTRVD\nSPAV\nCONEN")

        with open("metrics.data", "r") as entrada:
            for line in entrada:
                line = line.strip().replace(" ", "")
                if line[0] == "#":
                    continue
                self.metrics[line] = True

    def readConfigurationParameters(self):
        # TODO ler outro parametro do arquivo de configuracao
        if os.path.exists("config.data"):
            with open("config.data", "r") as entrada:
                self.configurationParameters = ConfigurationParameters()
                line = entrada.readline()
                line = line.split(" ")
                self.configurationParameters.communicationRadius = float(line[1])
        else:
            print("Configuration file not found! Recreating!")
            cp = ConfigurationParameters()
            cp.recreateConfigurationFile()

a = Principal()
a.main(sys.argv[1:])
