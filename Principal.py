from ConfigurationParameters import ConfigurationParameters
from Parser import Parser
from Extractor import Extractor
from Classifier import Classifier
import sys
import os
from Bar import Bar

class Principal:
 
    def __init__(self):
        self.readConfigurationParameters()

    def main(self, args):
        self.readConfigurationParameters()
        parser = None
        extractor = None

        if len(args) < 2:
            print("+--------------------------------------------------------------------------+")
            print("|                                                                          |")
            print("|                                                                          |")
            print("|    ( (                                                                   |")
            print("|    _)_)_                                                                 |")
            print("|  c(  M  )     MOCHA: a tool for MObility CHaracteristics Analysis        |") 
            print("|  ,-\___/-.                                                               |")
            print("|  `-------'                                                               |")
            print("|                                                                          |")
            print("| Usage: Principal.py ['-p', '-e', '-pe'] ['-r', '-s', '-n'] filename      |")
            print("|                                                                          |")
            print("| ['-p', '-e', '-pe']: parse, extract, or parse and extract                |")
            print("| ['-r', '-s', '-n' ]: RAW, SWIM or NS2 (if parsing)                       |")
            print("| filename        : file to be parsed/processed                            |")
            print("|                                                                          |")
            print("+--------------------------------------------------------------------------+")

        else:
            # Parse trace
            parser = Parser(self.configurationParameters.communicationRadius)

            if args[0] == "-p":
                if args[1] == "-r":
                    parser.parseRaw(args[2])
                elif args[1] == "-s":
                    parser.parseSwim(args[2])
            
            # Extract characteristics
            elif args[0] == "-e":

                parser.collectMaxes(args[1])
                extractor = Extractor(args[1], parser.maxT, parser.maxX, parser.maxY, self.configurationParameters.communicationRadius, parser.filesize)
                extractor.extract()
                classifier = Classifier()
                classifier.classify()

            # Parse and extract characteristics
            elif args[0] == "-pe":

                if args[1] == "-r":
                    newFile = parser.parseRaw(args[2])
                
                elif args[1] == "-s":   
                    newFile = parser.parseSwim(args[2])
                
                elif args[1] == "-n":      
                    newFile = parser.parseNS2(args[2])
                
                extractor = Extractor(newFile, parser.maxT, parser.maxX, parser.maxY, self.configurationParameters.communicationRadius, parser.filesize)
                extractor.extract()
                classifier = Classifier()
                classifier.classify()
                
 
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