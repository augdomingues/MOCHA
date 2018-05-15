from ConfigurationParameters import ConfigurationParameters
from Parser import Parser
from Extractor import Extractor
import sys

class Principal:
 
    def __init__(self):
        pass

    def main(self, args):
        self.readConfigurationParameters()
        parser = None
        extractor = None
        
        if args[0] == "p":
            if args[1] == "r":
                parser = Parser(self.configurationParameters.communicationRadius)
                parser.parseRaw(args[2])
                self.progressPercentage(100, 100)
            elif args[1] == "s":
                parser = Parser(self.configurationParameters.communicationRadius)
                parser.parseSwim(args[2])
                self.progressPercentage(100, 100)
        elif args[0] == "e":
            parser = Parser(self.configurationParameters.communicationRadius)
            parser.collectMaxes(args[1])
            extractor = Extractor(args[1], parser.maxT, parser.maxX, parser.maxY, self.configurationParameters.communicationRadius, parser.filesize)
            extractor.extract()
            self.progressPercentage(100, 100)
            # CHAMAR CLASSIFICADORRRR
        elif args[0] == "pe":
            if args[1] == "r":
                parser = Parser(self.configurationParameters.communicationRadius)
                newFile = parser.parseRaw(args[2])
                extractor = Extractor(newFile, parser.maxT, parser.maxX, parser.maxY, self.configurationParameters.communicationRadius, parser.filesize)
                extractor.extract()
                self.progressPercentage(100, 100)
                # CHAMAR CLASSIFICADORRRR
            elif args[1] == "s":   
                parser = Parser(self.configurationParameters.communicationRadius)
                newFile = parser.parseSwim(args[2])
                extractor = Extractor(newFile, parser.maxT, parser.maxX, parser.maxY, self.configurationParameters.communicationRadius, parser.filesize)
                extractor.extract()
                self.progressPercentage(100, 100)
                # CHAMAR CLASSIFICADORRRR
            elif args[1] == "n":      
                parser = Parser(self.configurationParameters.communicationRadius)
                newFile = parser.parseNS2(args[2])
                extractor = Extractor(newFile, parser.maxT, parser.maxX, parser.maxY, self.configurationParameters.communicationRadius, parser.filesize)
                extractor.extract()
                self.progressPercentage(100, 100)
                # CHAMAR CLASSIFICADORRRR
                
 
    def readConfigurationParameters(self):
        # TODO ler outro parametro do arquivo de configuracao
        try:
            inn = open("config.data")
            try:
                self.configurationParameters = ConfigurationParameters()
                line = inn.readline()
                split = line.split(" ")
                self.configurationParameters.communicationRadius = float(split[1])
                inn.close()
            except e:
                print("Configuration file incorrect!\nRecreating")
                self.configurationParameters.recreateConfigurationFile()
                print(e)
        except:
            print("Configuration file not found!\nRecreating!")
            cp = ConfigurationParameters()
            cp.recreateConfigurationFile()
 
    def progressPercentage(self, remain, total):
        if remain > total:
            raise ValueError('IllegalArgumentException')
        maxBareSize = 1 # 10unit for 100%
        remainProcent = ((100 * remain) / total) / maxBareSize
        defaultChar = '-'
        icon = "*"
        bare = ""
        for i in range (0, maxBareSize):
            bare += defaultChar
        bare += "]"
        bareDone = "["
        for i in range (0, int(remainProcent)):
            bareDone += icon
        bareRemain = bare[int(remainProcent): len(bare)]
        print(chr(27) + "[2J")
        print("\r" + bareDone + bareRemain + " " + str(remainProcent * 10) + "%")

        if remain == total:
            print("\n")

a = Principal()
a.main(sys.argv[1:])