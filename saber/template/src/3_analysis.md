
```python
import numpy as np
import pandas as pd
import json
import os.path as op
```

```python
report = json.load(open(op.join("..", "report.json")))
```

```python
df = pd.read_csv(op.join('..', 'data', report["last_date_full_data"],
                         '_', report['experiment_slug'], '.csv'))
branches = np.unique(df['branch']).tolist()
metrics = np.unique(df['metric']).tolist()
```

## Summary Plots
```{r}
lapply(summary_list, helper_funcs.create_plot)
```

## Decile Plots

```{r}
lapply(summary_list, helper_funcs.plot_pct_changes_decile)
```

## Tables

```{r}
tagList(lapply(summary_list, helper_funcs.create_table))
```
