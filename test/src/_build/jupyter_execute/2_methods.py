# Methods

import numpy as np
import pandas as pd
import json
import os.path as op
from myst_nb import glue

report = json.load(open(op.join("..", "report.json")))

df = pd.read_csv(op.join('..', 'data',
                 f"{report['last_date_full_data']}_{report['experiment_slug']}.csv"))

branches = np.unique(df['branch']).tolist()
metrics = np.unique(df['metric']).tolist()

glue('n_branches', len(branches))
glue('branches', branches)
glue('n_metrics', len(metrics))
glue('metrics', metrics)

## Supporting Assets

glue('experimenter_url', op.join('https://experimenter.services.mozilla.com',
                                 'experiments',
                                 report['experimenter_name']))

- Experimenter: {glue:text}`experimenter_url`


## Terminology

For this study, we used the following terms for our analysis:

__DS to complete__

## Data Assets
This experiment launched on {glue:text}`report['start_date']`, and targeted {glue:text}`report['target_percent']` of Firefox Users on version {glue:text}`report['versions']`. These users were randomly sampled and assigned one of the {glue:text}`n_branches` experimental conditions: {glue:text}`branches`.

We evaluated {glue:text}`n_metrics` measures of interactions in this study on a `per user` basis:

print('\n'.join(metrics))