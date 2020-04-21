# SABER

This is an MVP of the SABER framework.

To setup:

* Run `python setup.py develop`
	* This will check and/or install `mozanalysis` and its dependencies
* Install [Google Cloud SDK](https://cloud.google.com/sdk/install)
	* This will allow you to authenticate your session with your LDAP credentials
* Install R/[RMarkdown](https://bookdown.org/yihui/rmarkdown/installation.html).
* Create a new experiment folder under the `experiments` directory, i.e `experiments/my_new_experiment`

For your experiment:

* Create a `report.json` spec like the one below:
```json
{
    "title": "Pref-Flip Experiment: Separate Search default in Private Browsing",
    "publish_date": "2020-03-25",
    "author": "Teon L Brooks",
    "email": "teon@mozilla.com",
    "experiment_slug": "pref-separate-search-default-in-private-browsing-release-71-73-bug-1603606",
    "file": "index.html"
}
```


* Create a `experiment.json` spec like the one below:

```json
{
  "experimenter_name": "separate_search_default_pbm",
  "start_date": "2019-12-17",
  "last_date_full_data": "2020-02-18",
  "num_dates_enrollment": 1,
  "analysis_start_days": 0,
  "analysis_length_days": 2,
  "n_resamples": 1000,
  "target_percent": 0.2,
  "versions": "",
  "dataset_id": "teon",
  "metrics": [
    "search_count",
    "searches_with_ads",
    "tagged_search_count",
    "tagged_follow_on_search_count",
    "ad_clicks",
    "organic_search_count",
    {
      "search_clients_daily": {
      "separate_search_engine": [
              "ANY_VALUE(CASE WHEN default_search_engine =",
              "default_private_search_engine",
              "or default_private_search_engine is null THEN 0",
              "ELSE 1 END)"
      ],
      "subsession_hours_sum": "ANY_VALUE(subsession_hours_sum)",
      "active_hours_sum": "ANY_VALUE(active_hours_sum)"
      }
    }
  ]
}

```

* Fill in the relevant fields for your study.`dir` is the name of the directory you just created (in this case, "my_new_experiment")
* From the top level directory, run the following command

```bash
$ saber -p experiments/my_new_experiment
```

That's it! This will grab your data, aggregate it, generate bootstrapped statistics, and render the scaffolding for a report. The report should be edited as needed to properly communicate the results.
