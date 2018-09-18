class ConfigurationParameters:
    """ Represents the configuration parameters for the trace parsing. """

    def __init__(self):
        pass

    def recreateConfigurationFile(self):
        out = open('config.txt', 'w')
        try:
            out.write("CommunicationRadius 10")
            out.close()
        except:
            print("Error recreating configuration file!")
