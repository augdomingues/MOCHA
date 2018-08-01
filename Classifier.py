import subprocess
import os
import math
import warnings
import numpy as np
import scipy.stats as st
import sys
from Bar import Bar


class Classifier:

    def __init__(self, filename):
        self.files = ["CODU", "INCO", "EDGEP",
                      "TOPO", "RADG", "VIST", "TRVD", "SPAV", "CONEN"]
        self.barra = os.sep
        self.filename = filename.split(".")[0].replace("_parsed", "")
        self.filename += "_metrics_folder{}".format(self.barra)
        self.metrics = {}

    def best_fit_distribution(self, data, filename, bins=200, ax=None):
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

        bar = Bar(len(DISTRIBUTIONS), "Fitting {}".format(metric))
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
            bar.progress()

        print(" Fit to {} with params [{}]".format(best_distribution.name,
              best_params), end="")
        bar.finish()
        return (best_distribution.name, best_params)

    def classify(self):
        with open("{}fittedMetrics.txt".format(self.filename), "w+") as saida:
            for f in self.files:
                f = "{}{}.txt".format(self.filename, f)
                if os.path.exists(f):
                    data = np.genfromtxt(f, delimiter=",")
                    if data is None:
                        continue
                    if len(data) == 0:
                        input("File '{}' is empty. Press Enter to proceed to next metric. ".format(f))
                        continue
                    # Remove the IDs if they exist
                    if len(data.shape) == 2:
                        data = data[:, 1]
                    name, params = self.best_fit_distribution(data, f)
                    metricName = f
                    saida.write("{},{},{}\n".format(metricName, name, params))
                    self.metrics[metricName] = (name, params)
        return self.metrics

