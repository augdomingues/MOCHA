import os
import sys
import threading
from joblib import Parallel,delayed
import multiprocessing
from multiprocessing import Process, Manager, Value
import time


class Extractor:

    def __init__(self, infile, metrics, reportID=False, blocking=[]):
        self.infile = infile
        self.folder = infile.replace(".csv", "").replace(".txt", "")
        self.folder = self.folder.replace("_parsed", "")
        self.folder += "_metrics_folder{}".format(os.sep)
        self.kwargs = {"radius": 0.1}
        self.blocking_metrics = blocking

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.metrics = metrics
        self.reportID = reportID

    def addFilesForFitting(self):
        with open("filesForFitting.txt", "w+") as fit:
            for m in self.metrics:
                fit.write("{}{}.txt\n".format(self.folder, m))


    def processMetric(self, m):

        outfile = "{}{}{}.txt".format(self.folder, os.sep, m)

        # Import module
        metricClass = __import__("Metrics.{}".format(m))
        metricClass = getattr(metricClass, m)
        metricClass = getattr(metricClass, m)
        # metricClass = __import__(m)
        # metricClass = getattr(metricClass, m)

        # Create object metric and extract
        obj = metricClass(self.infile, outfile, self.reportID, **self.kwargs)
        obj.extract()

        # Obtain return structures, if any
        r = obj.commit()
        self.kwargs = {**self.kwargs, **r}

        # Write values to file
        obj.print()


    def extract(self):
        self.blocking_metrics = ["SPAV", "TOPO", "EDGEP"]
        for b in self.blocking_metrics:
            self.processMetric(b)

        for m in self.metrics:
            p = Process(target=self.processMetric, args=(m,))
            p.start()




#for m in metrics:
#    a = threading.Thread(target=process_metric, args=(m, ))
#    a.start()
#    a.join()

#num_cores = multiprocessing.cpu_count()
#num_cores = len(metrics)
#print("Processing with {} cores".format(num_cores))
#Parallel(n_jobs = num_cores)(delayed(process_metric)(m) for m in metrics)
#Parallel(n_jobs = num_cores - 1)(delayed(mapMatching)(int(i)) for i in taxi_names)


