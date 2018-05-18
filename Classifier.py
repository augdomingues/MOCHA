import subprocess
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
        
        bar = Bar(len(DISTRIBUTIONS), "Fitting {}".format(filename))
        # Estimate distribution parameters from data
        for distribution in DISTRIBUTIONS:
            bar.progress()
            # Try to fit the distribution
            try:
                # Ignore warnings from data that can't be fit
                with warnings.catch_warnings():
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
     
                     
     
                    # identify if this distribution is better
                    if -2*log(sse)+2*(len(params) + 1) < best:
                        best_distribution = distribution
                        best_params = params
                        best = -2*log(sse)+2*(len(params) + 1)
     
            except Exception:
                pass
        bar.finish()
        return (best_distribution.name, best_params)

    def __init__(self,filename):
        self.filename = filename

    def classify(self):
        with open(self.filename, "r") as entrada:
            for line in entrada:
                line = line.strip()
                data = np.genfromtxt(line)
                name,params = self.best_fit_distribution(data,line)
                print("Fitted {} to {} with params [{}]".format(line,name,params))