from google.cloud import bigquery
from py_utils.utils import read_sql_query, read_json, construct_table_name
from py_utils.stats import process_experiment
import json
import re
import sys

experiment_dir = sys.argv[1]
spec = read_json(experiment_dir + "/experiment.json")

# define the various projects and paths
# to access the already-dervied experiment dataset
# generated from derive_experiment.py
client = bigquery.Client()
dataset_id = "analysis"
table_name = construct_table_name(spec)
table_ref = client.dataset(dataset_id).table(table_name)
derived_experiment_table_name = ".".join([table_ref.project, dataset_id, table_name])

# read in sql and inject table_name
# (BQ forbids table names to be formal parameters,
#  must use str.format here)
sql_query_by_client = (
  read_sql_query("exp_by_client.sql").format(derived_experiment_table_name)
)

sql_query_by_branch = (
  read_sql_query("exp_by_branch.sql").format(derived_experiment_table_name)
)


print("Running the following query:")
print(sql_query_by_client)
# Start the query
query_job = client.query(sql_query_by_client)
# collect result to pandas dataframe
exp_by_client = query_job.to_dataframe()
# bootstrap the metrics
process_experiment(exp_by_client, 100, spec)

print("Running the following query:")
print(sql_query_by_branch)

query_job = client.query(sql_query_by_branch)
# collect result to pandas dataframe
exp_by_branch = query_job.to_dataframe()
exp_by_branch.to_csv("./{}/data/branch_day.csv".format(experiment_dir), index=False)