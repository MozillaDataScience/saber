# Methods

```python
import numpy as np
import pandas as pd
import json
import os.path as op
```

```python
report = json.load(open(op.join("..", "report.json")))
```

### Supporting Assets
- [Experimenter]({glue:text}`f'https://experimenter.services.mozilla.com/experiments/{report['experimenter_name']}'`)

### Terminology

For this study, we used the following terms for our analysis:

__DS to complete__

### Data Assets
This experiment launched on {glue:text}`report['start_date']`, and targeted {glue:text}`report['target_percent']` of Firefox Users on version {glue:text}`report['version']`. These users were randomly sampled and assigned one of the {glue:text}`len(branches)` experimental conditions: {glue:text}`branches`.

We evaluated {glue:text}`length(metrics)` measures of interactions in this study on a `per user` basis:

```{r}
knitr::kable(unique(df['metric']), col.names='Metrics')
```


```{r}
summary_list <- helper_funcs.create_summary_list(df)
```