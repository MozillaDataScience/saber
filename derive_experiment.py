from google.cloud import bigquery
from py_utils.utils import read_sql_query, read_json, construct_table_name
import sys

experiment_dir = sys.argv[1]

print("Reading the experiment spec from " + experiment_dir)
# load the experiment specification
spec = read_json(experiment_dir + "/experiment.json")

# boilerplate BQ setup
client = bigquery.Client()
dataset_id = "analysis"
table_name = construct_table_name(spec)
table_ref = client.dataset(dataset_id).table(table_name)

# prepare the spec parameters for insertion into SQL
query_params = [
    bigquery.ScalarQueryParameter("experiment_slug", "STRING", spec["experiment_slug"]),
    bigquery.ScalarQueryParameter("start_date", "STRING", spec["start_date"]),
    bigquery.ScalarQueryParameter("end_date", "STRING", spec["end_date"]),
    bigquery.ScalarQueryParameter(
        "enrollment_end_date", "STRING", spec["enrollment_end_date"]
    ),
]

# define the job configuration for the query
# set params and output destination for the experiment's master
# dataset
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
job_config.destination = table_ref
job_config.write_disposition = (
    bigquery.WriteDisposition.WRITE_TRUNCATE
)  # allows for overwriting

# read in query scaffolding
sql_query = read_sql_query("experiment_master.sql")

# Start the query, passing in the extra configuration.
# This fills in the query, and sets the destination,
# and permissions for overwritting
query_job = client.query(sql_query, job_config=job_config)

print("Running the following query:\n")
print(sql_query)
print("\nwith the following parameters:")
for i in query_params:
	print(i)

query_job.result()  # Waits for the query to finish

# The query result is now directly queryable for downstream analysis
print("\nQuery results loaded to table {}".format(table_ref.path))
