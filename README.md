<p align="center">
    <img width="160" src="docs/logo.png">
</p>

# NiceTrace

NiceTrace is a Python module for user-friendly structured tracing and elegant display of resulting traces. 
While designed for generic usage, it's particularly well-suited for tracing experiments with Large Language Models (LLMs).

<p align="center">
    <img width="100%" src="docs/nicetrace_screenshot.png">
</p>

## Installation

```bash
# For tracing only
pip install nicetrace

# For tracing & displaying traces
pip install nicetrace[server]
```

## Getting started

Here's how to create a simple trace and write it to a JSON file:

```python
from nicetrace import trace, FileWriter

with FileWriter("traces/my_trace.json"):
    with trace("Root node"):
        with trace("Child node", inputs={"x": 10, "y": 20}) as node:
            node.add_output("", "Hello world!")
```

To start a traceview server over the `traces` directory:

```commandline
python3 -m nicetrace.server traces
```

Then, open your web browser and navigate to http://localhost:4090 to view your traces.


<p align="center">
    <img width="80%" src="docs/helloworld_screenshot.png">
</p>

