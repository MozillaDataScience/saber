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
# Results


```{code-cell} ipython3
:tags: [remove-cell]

import numpy as np
import pandas as pd
import plotly.express as px
import json
import os.path as op
from myst_nb import glue


report = json.load(open(op.join("..", "report.json")))
df = pd.read_csv(op.join('..', 'data',
                 f"{report['last_date_full_data']}_{report['experiment_slug']}.csv"))
```

## Summary Plots
```{code-cell} ipython3
:tags: [hide-cell]

alpha_level = 0.05
ci  = list(map(str, [alpha_level/2, 1 - (alpha_level/2)]))

rel_uplift = df[df['analysis'] == 'rel_uplift']
# figure out why there are nans in the results
rel_uplift.fillna(0, inplace=True)

rel_uplift['sig'] = np.sign(rel_uplift[ci[0]] * rel_uplift[ci[1]])
rel_uplift[rel_uplift['sig'] == 0]['sig'] = -1

rel_uplift.rename(columns={ci[0]: 'lower_ci', ci[1]: 'upper_ci'}, inplace=True)
rel_uplift['diff_lower_ci'] = rel_uplift['mean'] - rel_uplift['lower_ci']
rel_uplift['diff_upper_ci'] = rel_uplift['upper_ci'] - rel_uplift['mean']
branches = np.unique(rel_uplift['branch'])

# create separate plots by branch comparison
summary_groupby = rel_uplift.groupby('branch')
```

```{code-cell} ipython3
:tags: [hide-input]

for ii, group in summary_groupby:
    group_mean = group[group['statistic'] == 'expected_mean']
    fig = px.scatter(group_mean, y='metric', x='mean',
                     error_x_minus='diff_lower_ci', error_x='diff_upper_ci',
                     title=ii)
    fig.show()
```

## Decile Plots

```{code-cell} ipython3
:tags: [hide-input]

for ii, group in summary_groupby:
    group_deciles = group[group['statistic'] != 'expected_mean']
    fig = px.scatter(group_deciles, y='statistic', x='mean',
                     error_x_minus='diff_lower_ci', error_x='diff_upper_ci',
                     facet_col='metric', facet_col_wrap=3, range_x=[-.1, .1],
                     title=ii, labels={'statistic': 'decile', 'mean': '% change'})
    fig.show()
```

## Tables

```{code-cell} ipython3
:tags: [hide-input]

import plotly.graph_objects as go
for ii, group in summary_groupby:
    group_mean = group[group['statistic'] == 'expected_mean']
    group_mean['mean'] = group_mean['mean'].map('{:.2f}%'.format)
    group_mean['Confidence Interval'] = (f"{(1-alpha_level)* 100:2.0f}% CI[" +
                                          group_mean['lower_ci'].map('{:.2f}'.format) +
                                          ', '
                                          + group_mean['upper_ci'].map('{:.2f}'.format) +
                                          ']')
    group_mean.rename(columns={'mean': 'Percentage Change',
                                'metric': 'Metric of Interest'}, inplace=True)
    group_mean = group_mean[['Metric of Interest',
                              'Percentage Change',
                              'Confidence Interval']]
    fig = go.Figure(data=go.Table(
                    header=dict(values=list(group_mean.columns),
                                align='center'),
                    cells=dict(values=list(zip(*group_mean.values.tolist())),
                                align='center')),
                    layout=dict(title=ii))
    fig.show()
```
