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
```{code-cell} ipython3
:tags: [remove-cell]

from myst_nb import glue
import numpy as np
import pandas as pd
import json
import os.path as op


report = json.load(open(op.join("..", "report.json")))
# hack to add all the report keys to the glue scope
for key in report:
    glue(f"report['{key}']", report[key])
```
# Executive Summary
{glue:text}`report['author']` <{glue:text}`report['email']`>
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
