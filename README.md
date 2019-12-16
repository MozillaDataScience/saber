# SABER

This is an MVP of the SABER framework.

To run locally

* Ensure you have GCP credentials and point to them in the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
* Install the [BigQuery client library for python](https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python).
* Install R/[RMarkdown](https://bookdown.org/yihui/rmarkdown/installation.html).
* Create a new experiment folder under the `experiments` directory, i.e `experiments/my_new_experiment`
* Create a specification JSON file like the one below

```json
{
	"author": "bmiroglio",
	"experiment_slug": "my_experiment_slug_bug_xxxxx",
	"report_title": "My Experiment Title",
	"start_date": "2019-09-03",
	"end_date": "2019-10-29",
	"enrollment_end_date": "2019-09-17",
	"treatment_branch_name": "treatment",
	"control_branch_name": "control",
	"target_percent": "1%",
	"channels": "release",
	"versions": "70",
	"metrics": [
		"sap",
		"tagged_sap",
		"ad_clicks",
		"organic"
	]
}
```

* Fill in the relevant fields for your study.`dir` is the name of the directory you just created (in this case, "my_new_experiment")
* From the top level directory, run the following command

```bash
$ bash run.sh experiments/my_new_experiment
```

That's it! This will grab your data, aggregate it, generate bootstrapped statistics, and render the scaffolding for a report. The report should be edited as needed to properly communicate the results. 
