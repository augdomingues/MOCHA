import os

class ConfigurationParameters:
    """ Represents the configuration parameters for the trace parsing. """

    communicationRadius = 0
    distanceFunction = ""

    def __init__(self):
        if os.path.exists("config.txt"):
            with open("config.txt", "r") as entrada:
                line = entrada.readline().split()
                ConfigurationParameters.communicationRadius = float(line[1])
                line = entrada.readline().split()
                ConfigurationParameters.distanceFunction = line[1]
        else:
            self.recreateConfigurationFile()

    def recreateConfigurationFile(self):
        out = open('config.txt', 'w')
        try:
            out.write("CommunicationRadius 10\n")
            out.write("DistanceFunction haversine")
            out.close()

            ConfigurationParameters.communicationRadius = 10
            ConfigurationParameters.distanceFunction = "haversine"
        except:
            print("Error recreating configuration file!")
