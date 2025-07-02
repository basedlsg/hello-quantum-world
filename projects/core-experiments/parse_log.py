import json
from src.maxcut_implementations.canonical_maxcut import CanonicalMaxCut
import networkx as nx
from collections import Counter

# Define the graph used in the experiment
graph = nx.Graph()
graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
maxcut_calculator = CanonicalMaxCut(graph)

# Load the results from the AWS log file
with open('aws_cloud_result.json', 'r') as f:
    log_data = json.load(f)

# The log file contains a list of individual measurements.
# We need to first convert this into a histogram of counts.
raw_measurements = log_data['measurements']
# Convert each measurement array (e.g., [0, 1, 1]) into a bitstring (e.g., '011')
bitstrings = ["".join(map(str, m)) for m in raw_measurements]
measurement_counts = Counter(bitstrings)

total_shots = log_data['taskMetadata']['shots']

# Calculate the expectation value from the measurement counts
classical_cut_total = 0
for bitstring, count in measurement_counts.items():
    cut_value = maxcut_calculator.calculate_cut_value(bitstring)
    classical_cut_total += cut_value * count

final_expectation_value = classical_cut_total / total_shots

# Print the analyzed results
print('--- AWS Cloud Execution Log Analysis ---')
print(f'Task ARN: {log_data["taskMetadata"]["id"]}')
print(f'Total Shots: {total_shots}')
print(f'Final Calculated Expectation Value: {final_expectation_value:.6f}')
print('\nMeasurement Distribution:')
for bitstring, count in sorted(measurement_counts.items()):
    print(f'  - State |{bitstring}>: {count} counts') 