# Waterfall Chart in Python
---

The waterfall_ax library creates flexible waterfall charts based on matplotlib. 

It provides flexible controls over your plot. For details please refer to the [waterfall_ax repo](https://github.com/microsoft/waterfall_ax).

## A Simple Example

Sample code:

```
from waterfall_ax import WaterfallChart

# Cumulative values
step_values = [80, 70, 90, 85, 60, 50]

# Plot
waterfall = WaterfallChart(step_values)
wf_ax = waterfall.plot_waterfall(title='A Simple Example')
```
