# MOCHA
MOCHA is a Tool for MObility CHAracteristics extraction. It can be used to extract information from mobility traces.

# How to use
 - Use -pr to parse a RAW trace or -ps to parse a SWIM trace
 - Use -e to extract the metrics from the parsed trace
 - Use -c to classify each metric according to its distribution
 - Use -id to add each user ID to the metrics report ( NOT TO BE USED WITH -c )
 - The order of the parameters doesn't matter, as long as the filename is the last parameter
```sh
$ python3 Mocha.py -pr -e -c mytrace.csv # Parse, extract and classify the RAW trace mytrace.csv
$ python3 Mocha.py -e mytrace_parsed # Extract the metrics from mytrace_parsed.csv
$ python3 Mocha.py -c mytrace_parsed # Classify the metrics
$ python3 Mocha.py -id -e mytrace_parsed # Extract metrics with respective users' IDs
```
