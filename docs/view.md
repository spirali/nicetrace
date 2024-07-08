
For storing a traces you may use `FileWriter` and `DirWriter`. 
They both stores traces in JSON format. The both saves traces when
they are still running so you can observe also running process.

## FileWriter

`FileWriter` stores trace into a single file.

```python
from nicetrace import trace, FileWriter

with FileWriter("traces/my_trace.json"):
    
    # Stores the root node and its children into 'my_trace.json'
    with trace("Root node"):
        with trace("Child node"):
            pass
    
```

If more root nodes are created, then `FileWriter` overrides the previous content.

```python
with FileWriter("traces/my_trace.json"):
    
    # Stores a root node in my_trace.json
    with trace("Root node"):
        pass

    # Overwrite my_trace.json with a new root node
    with trace("Root node"):
        pass

```

## DirWriter


`FileWriter` stores traces into JSON into a given directory.
Traces are stored under name `trace-<UID>.json`. 


```python
from nicetrace import trace, DirWriter

with DirWriter("traces"):
    
    # Stores the node and its child in file trace f"trace-{root1.uid}.json"
    with trace("Root node") as root1:
        with trace("Child node"):
            pass

    # Stores the node and its child in file trace f"trace-{root2.uid}.json"
    with trace("Root node") as root2:
        pass

```

## Running a live trace view over a directory

If you install NiceTrace with feature `server` (`pip install nicetrace[server]`)
then you can run a HTTP server over a directory. It does not matter if trace files were created via `FileWriter` or `DirWriter`.

```commandline
python3 -m nicetrace.server <DIRECTORY_WITH_TRACES>
```

Then, open your web browser and navigate to http://localhost:4090 to view your traces.


## Saving a trace as static HTML file.

```python
from nicetrace import trace, write_html

with trace("Root node") as node:
    with trace("Child 1"):
        pass

write_html(node, "out.html")
```

It creates a stand-alone HTML file that captures an immediate state of the trace.
The content will not be automatically updated if trace is changed.