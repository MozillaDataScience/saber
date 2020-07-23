# SABER

This is an MVP of the Swift A/B Experiment Report (SABER) framework.

To setup:

* Install [Google Cloud SDK](https://cloud.google.com/sdk/install)
	* This will allow you to authenticate your session with your LDAP credentials
* Run `python setup.py develop`
	* This will check and/or install `mozanalysis`, `jupyter-book` and its dependencies
* Create a new experiment folder under your `experiments` directory, i.e `experiments/my_new_experiment`

For your experiment:

* Create a `report.json` spec like the one below:
```json
{
    "title": "Pref-Flip Experiment: Firefox Awesome Feature",
    "publish_date": "1970-04-25",
    "author": "Data Scientist",
    "email": "ds@mozilla.com",
    "experiment_slug": "pref-firefox-awesome-feature-release-75-77-bug-1603606",
    "file": "index.html",
    "experimenter_name": "separate_search_default_pbm",
    "start_date": "1970-01-01",
    "last_date_full_data": "1970-03-31",
    "num_dates_enrollment": 14,
    "analysis_start_days": 0,
    "analysis_length_days": 28,
    "n_resamples": 1000,
    "target_percent": 0.2,
    "versions": "75-77",
    "dataset_id": "ds",
    "metrics": [
      "search_count",
      "searches_with_ads",
      "tagged_search_count",
      "tagged_follow_on_search_count",
      "ad_clicks",
      "organic_search_count"
    ],
    "user_defined_metrics": {
      "events": {
        "awesomeness": "COUNT_IF(event_type = 'awesome')"
      }
    }
  }
```

```

* Fill in the relevant fields for your study. `dir` is the name of the directory you just created (in this case, "my_new_experiment")
* From the top level directory, run the following command

```bash
$ saber -p experiments/my_new_experiment
```

That's it! This will grab your data, aggregate it, generate bootstrapped statistics, and render the scaffolding for a report. The report should be edited as needed to properly communicate the results.
