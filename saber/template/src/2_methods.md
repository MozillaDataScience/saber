---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: '0.9'
    jupytext_version: 1.5.2
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Methods

```{code-cell} ipython3
:tags: [remove-cell]

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
```


## Supporting Assets

```{code-cell} ipython3
# glue('experimenter_url', op.join('https://experimenter.services.mozilla.com',
#                                'experiments',
#                                report['experimenter_name']))
op.join('https://experimenter.services.mozilla.com',
        'experiments',
        report['experimenter_name'])
```

<!-- - [Experimenter]({glue:text}`experimenter_url`)
<a href ={glue:text}`experimenter_url`>Experimenter</a> -->

## Terminology

For this study, we used the following terms for our analysis:

__DS to complete__

## Data Assets
This experiment launched on {glue:text}`report['start_date']`, and targeted {glue:text}`report['target_percent']` of Firefox Users on version {glue:text}`report['versions']`. These users were randomly sampled and assigned one of the {glue:text}`n_branches` experimental conditions: {glue:text}`branches`.

We evaluated {glue:text}`n_metrics` measures of interactions in this study on a `per user` basis:

```{code-cell} ipython3
:tags: [remove-input]
print('\n'.join(metrics))
```
