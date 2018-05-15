class ConfigurationParameters:

    def __init__(self):
        pass
 
    def recreateConfigurationFile(self):
        out = open('config.data','w')
        try:
            out.write("CommunicationRadius 35")
            out.close()
        except:
            print("Error recreating configuration file!")