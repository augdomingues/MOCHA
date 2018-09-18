"""
    Class to classify metrics according to their statistical distributions
"""
import os
import math
import warnings
import numpy as np
import scipy.stats as st
from Bar import Bar


class Classifier:
    """
        Class to classify metrics according to their statistical distributions
    """

    def __init__(self, filename):
        """ Initiate structures in the class. """
        self.files = ["CODU", "INCO", "EDGEP",
                      "TOPO", "RADG", "VIST", "TRVD", "SPAV", "CONEN"]
        self.barra = os.sep
        self.filename = filename.split(".")[0].replace("_parsed", "")
        self.filename += "_metrics_folder{}".format(self.barra)
        self.metrics = {}

    def best_fit_distribution(self, data, filename, bins=200):
        """ Computes and returns the distribution that best fits the data. """
        y, x = np.histogram(data, bins=bins, density=True)
        x = (x + np.roll(x, -1))[:-1] / 2.0

        DISTRIBUTIONS = [st.dweibull, st.expon, st.gamma, st.logistic,
                         st.lognorm, st.norm, st.pareto]

        best_distribution = st.norm
        best_params = (0.0, 1.0)
        best_sse = np.inf

        if os.sep in filename:
            metric = filename.split(os.sep)[1]
        else:
            metric = filename

        progressbar = Bar(len(DISTRIBUTIONS), "Fitting {}".format(metric))
        for distribution in DISTRIBUTIONS:
            warnings.filterwarnings('ignore')
            params = distribution.fit(data)
            arg = params[:-2]
            loc = params[-2]
            scale = params[-1]
            pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
            sse = np.sum(np.power(y - pdf, 2.0))
            sse = -2*math.log(sse)+2*(len(params) + 1)
            if sse < best_sse:
                best_distribution = distribution
                best_params = params
                best_sse = sse

            print(" SSE of {} is {}(Current best: {})"
                  .format(distribution.name, round(sse, 2),
                          round(best_sse, 2)), end="")
            progressbar.progress()

        print(" Fit to {} with params [{}]".format(best_distribution.name,
                                                   best_params), end="")
        progressbar.finish()
        return (best_distribution.name, best_params)

    def classify(self):
        """ Open the metrics to classify them. """
        with open("{}fittedMetrics.txt".format(self.filename), "w+") as saida:
            for f in self.files:
                f = "{}{}.txt".format(self.filename, f)
                if os.path.exists(f):
                    data = np.genfromtxt(f, delimiter=",")
                    if data is None:
                        continue
                    if len(data) == 0:
                        input("File '{}' empty. [Enter] to proceed.".format(f))
                        continue
                    # Remove the IDs if they exist
                    if len(data.shape) == 2:
                        data = data[:, 1]
                    name, params = self.best_fit_distribution(data, f)
                    metric_name = f
                    saida.write("{},{},{}\n".format(metric_name, name, params))
                    self.metrics[metric_name] = (name, params)
        return self.metrics
