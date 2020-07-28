# Executive Summary

from myst_nb import glue
import numpy as np
import pandas as pd
import json
import os.path as op


report = json.load(open(op.join("..", "report.json")))
# hack to add all the report keys to the glue scope
for key in report:
    glue(f"report['{key}']", report[key])

{glue:text}`report['author']` <{glue:text}`report['email']`>

Date: {glue:text}`report['publish_date']`

Status: <*automated draft*>

## Motivation
This is an experiment report for the {glue:text}`report['experiment_slug']` study.

__DS to complete__

## Takeaways

__DS to complete__

## Design

```{image} images/design.png
:alt: 'experiment mockup'
:width: 600px
:align: center
```

```{toctree}
:hidden:
:titlesonly:


2_methods
3_analysis
```