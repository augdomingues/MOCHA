import subprocess
import os
import math
import warnings
import numpy as np
import scipy.stats as st
import sys
from Bar import Bar
 
class Classifier:

    # Create models from data
    def best_fit_distribution(self, data, filename, bins=200, ax=None):
        """Model data by finding best fit distribution to data"""
        # Get histogram of original data
        y, x = np.histogram(data, bins=bins, density=True)
        x = (x + np.roll(x, -1))[:-1] / 2.0
     
        # Distributions to check
        DISTRIBUTIONS =[st.dweibull,st.expon,st.gamma,st.logistic,st.lognorm,st.norm,st.pareto]
     
        # Best holders
        best_distribution = st.norm
        best_params = (0.0, 1.0)
        best_sse = np.inf

        if "/" in filename:
            metric = filename.split("/")[1]
        elif "\\" in filename:
            metric = filename.split("\\")[1]
        else:
            metric = filename
        
        bar = Bar(len(DISTRIBUTIONS), "Fitting {}".format(metric))
        # Estimate distribution parameters from data
        for distribution in DISTRIBUTIONS:
            # Try to fit the distribution
            # Ignore warnings from data that can't be fit
            warnings.filterwarnings('ignore')

            # fit dist to data
            params = distribution.fit(data)

            # Separate parts of parameters
            arg = params[:-2]
            loc = params[-2]
            scale = params[-1]

            # Calculate fitted PDF and error with fit in distribution
            pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
            sse = np.sum(np.power(y - pdf, 2.0))
            sse = -2*math.log(sse)+2*(len(params) + 1)     # SSE with Akaike's Information Criteria

            # identify if this distribution is better
            if sse < best_sse:
                best_distribution = distribution
                best_params = params
                best_sse = sse
            
            print(" SSE of {} is {} (Current best: {})            ".format(distribution.name, round(sse,2), round(best_sse,2)), end="") 
            bar.progress()
                
        print(" Fit to {} with params [{}]".format(best_distribution.name,best_params),end="")
        bar.finish()
        return (best_distribution.name, best_params)

    def __init__(self,filename):
        self.barra = "\\" if os.name == 'nt' else "/"
        self.filename = filename.split(".")[0].replace("_parsed", "") + "_metrics_folder{}".format(self.barra)
        self.metrics = {}

    def classify(self):
        with open("{}fittedMetrics.txt".format(self.filename), "w+") as saida:
            with open("filesForFitting.txt", "r") as entrada:
                for line in entrada:
                    line = line.strip()
                    if "SOCOR" in line:
                        continue
                    data = np.genfromtxt(line)
                    if len(data) == 0:
                        input("File '{}' is empty. Press Enter to proceed to next metric. ")
                        continue
                    name,params = self.best_fit_distribution(data,line)
                    if "/" in line:
                        metricName = line.split("/")[1].replace(".txt", "")
                    elif "\\" in line:
                        metricName = line.split("\\")[1].replace(".txt", "")
                    saida.write("{},{},{}\n".format(metricName,name,params))
                    self.metrics[metricName] = (name,params)
        return self.metrics