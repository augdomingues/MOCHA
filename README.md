# MOCHA
MOCHA is a Tool for MObility CHAracteristics extraction. It can be used to extract social, spatial and temporal metrics from mobility traces. After that, MOCHA can extract the statistical distribution of the metrics, and you can use it to visually compare the distributions of metrics between two or more mobility traces. The metrics shipped in MOCHA are:

__Social Metrics__
 - CODU: Contact duration between a pair
 - INCO: Inter-contact time
 - EDGEP: Edge persistence between a pair
 - TOPO: Topological Overlap between a pair
 - CONEN: Contact Entropy (Computed as the Shannon's entropy)
 - MAXCON: Maximum number of connections in a interval *d* between a pair of users
 - SOCOR: Social Correlation of a trace
 
__Spatial Metrics__
 - TRVD: Travel distance of a user
 - RADG: Radius of gyration of a user
 - SPAV: Spatial variability (computed as the Shannon's entropy)
 
__Temporal Metrics__
 - VIST: Visit time of a user in a place

But you can also add your own metrics.

# Requirements
Python 3.+

# How to use

__Selecting the metrics__
- First, you must select the metric you want to parse in the file __Metrics.txt__. To disconsider a Metric, use __#__ before its name. 

__Adding your own metrics__
- To add your own metrics, you must create a class in the Metrics folder containing your metric. The class name must match exactly the metric name, and the class must implement the interface **Metric.py**, containing the methods **\_\_init\_\_**, **extract**, **print**, **explain**, and **commit**. Here's what they should do:
 - \_\_init\_\_(self, infile, outfile, reportID, \*\*kwargs): initialize the structures in the metric. *infile* and *outfile* are created based on the metric and trace name. *reportID* referes to the reporting of the entities ID's. Any data that is shared between multiple metrics must be passed through the *\*\*kwargs* parameters. No processing should be done in this method.
 - extract(self): opens the input file (*self.infile*) and extracts the metrics. All the heavy processing should be done here, but you can create additional methods to improve clarity and code structure. In order to measure the time of the extraction, you can add the decorator **@Metric.timeexecution** to this method.
 - print(self): outputs the metric to the output file (*self.outfile*). You should use a condition for the *self.reportID* variable to print or not the ID's.
 - explain(self): returns a string containing a explanation about what the metric is, for documentation purposes.
 - commit(self): if this metric will share any of its extracted values with another metrics, you should return them here as a dict, where the key is the name and the item is the data. If the metric does not share values, then just return an empty dict.

MOCHA uses processes to compute the metrics in parallel, so if any metric you implemented produces a result which other metrics depend on it, you should add a __\*__  right after its name. Metrics tagged with this symbol will be processed before in a non-parallel way. Any dependency between metrics in this group can be resolved by changing their order in the file (metrics that come first are processed first). 


__Parameters__
 - Use -pr to parse a RAW trace or -ps to parse a SWIM trace
 - Use -e to extract the metrics from the parsed trace
 - Use -c to classify each metric according to its distribution
 - Use -id to add each user ID (or a pair of ID's, depending on the metric) to the metrics report
 - The order of the parameters doesn't matter, but the filename MUST be the last parameter
 
__Examples__
```sh
$ python3 Mocha.py -pr -e -c mytrace.csv # Parse, extract and classify the RAW trace mytrace.csv
$ python3 Mocha.py -e mytrace_parsed # Extract the metrics from mytrace_parsed.csv
$ python3 Mocha.py -c mytrace_parsed # Classify the metrics
$ python3 Mocha.py -id -e mytrace_parsed # Extract metrics with respective users' IDs
```
