import pandas as pd
import numpy as np
import json

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import *
from evidently.test_suite import TestSuite
from evidently.tests import *

import os

root_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..'))
merged = os.path.join(root_dir, 'data', 'processed', 'current_data.csv')
referenced = os.path.join(root_dir, 'data', 'processed', 'reference_data.csv')
report_file = os.path.join(root_dir, 'reports', 'data_drift.html')
ds_file = os.path.join(root_dir, 'reports', 'data_stability.json')

csv1 = pd.read_csv(merged)
current = pd.DataFrame(csv1)
current.rename(columns={'pm10': 'target'}, inplace=True)
current['prediction'] = current['target'].values + \
    np.random.normal(0, 5, current.shape[0])
current = current.astype(int)

csv2 = pd.read_csv(referenced)
reference = pd.DataFrame(csv2)
reference.rename(columns={'pm10': 'target'}, inplace=True)
reference['prediction'] = reference['target'].values + \
    np.random.normal(0, 5, reference.shape[0])
reference = reference.astype(int)

report = Report(metrics=[
    DataDriftPreset(),
])
report.run(reference_data=reference, current_data=current)
report.save_html(report_file)


suite = TestSuite(tests=[
    TestNumberOfColumnsWithMissingValues(),
    TestNumberOfRowsWithMissingValues(),
    TestNumberOfConstantColumns(),
    TestNumberOfDuplicatedRows(),
    TestNumberOfDuplicatedColumns(),
    TestColumnsType(),
    TestNumberOfDriftedColumns(),
])
suite.run(reference_data=reference, current_data=current)
suite.as_dict()
print(suite)
