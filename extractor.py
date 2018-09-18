""" This module contains the class that performs the metrics extraction
    from the parsed trace.
"""
import os
from multiprocessing import Process


class Extractor:
    """ Class that performs the metrics' extraction steps. """

    def __init__(self, infile, metrics, report_id=False, blocking=None):
        self.infile = infile
        self.folder = infile.replace(".csv", "").replace(".txt", "")
        self.folder = self.folder.replace("_parsed", "")
        self.folder += "_metrics_folder{}".format(os.sep)
        self.kwargs = {"radius": 0.1}
        self.blocking_metrics = [] if blocking is None else blocking

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.metrics = metrics
        self.report_id = report_id

    def add_files_for_fitting(self):
        """ Adds fitted metrics to the fitted metrics file. """
        with open("filesForFitting.txt", "w+") as fit:
            for metric in self.metrics:
                fit.write("{}{}.txt\n".format(self.folder, metric))

    def process_metric(self, metric):
        """ Process a given metric. """
        outfile = "{}{}{}.txt".format(self.folder, os.sep, metric)

        # Import module
        metric_class = __import__("Metrics.{}".format(metric))
        metric_class = getattr(metric_class, metric)
        metric_class = getattr(metric_class, metric)

        # Create object metric and extract
        obj = metric_class(self.infile, outfile, self.report_id, **self.kwargs)
        obj.extract()

        # Obtain return structures, if any
        returned_structures = obj.commit()
        self.kwargs = {**self.kwargs, **returned_structures}

        # Write values to file
        obj.print()

    def extract(self):
        """ Organizes the parallel processing of the metrics. """
        # self.blocking_metrics = ["SPAV", "TOPO", "EDGEP"]
        for blocking in self.blocking_metrics:
            self.process_metric(blocking)

        for metric in self.metrics:
            process = Process(target=self.process_metric, args=(metric,))
            process.start()
