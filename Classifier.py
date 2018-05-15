import subprocess
import warnings
import numpy as np
import scipy.stats as st
import sys
 
class Classifier:

    # Create models from data
    def best_fit_distribution(self, data, bins=200, ax=None):
        """Model data by finding best fit distribution to data"""
        # Get histogram of original data
        print "danilo"
        y, x = np.histogram(data, bins=bins, density=True)
        x = (x + np.roll(x, -1))[:-1] / 2.0
     
        # Distributions to check
        DISTRIBUTIONS =[st.dweibull,st.expon,st.gamma,st.logistic,st.lognorm,st.norm,st.pareto]
     
        # Best holders
        best_distribution = st.norm
        best_params = (0.0, 1.0)
        best_sse = np.inf
     
        # Estimate distribution parameters from data
        for distribution in DISTRIBUTIONS:
            print("Fitting to " + str(distribution) + "\n")
            print ("...")
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
                print "oi"
                pass
     
        return (best_distribution.name, best_params)

    def __init__(self):
        try:
            print(" .....")

            filename = "dartmouth-parsed_codu.trace"
            data = np.genfromtxt(filename)
            print data
            name, params = self.best_fit_distribution(filename)
            print(str(name) + "  "  + str(params) + "\n")
            print ("...")
             
        except Exception, e:
            # TODO Auto-generated catch block
            print (e)

a = Classifier()