from .html.statichtml import get_static_html
from .html.staticfiles import copy_static_files
from nicetrace import TraceWriter, TracingNode
import uuid
import os
import json
from pathlib import Path


def _write_file(filename: str, data: str):
    tmp_filename = f".{uuid.uuid4().hex}.hex._tmp"
    try:
        with open(tmp_filename, "w") as f:
            f.write(data)
        os.rename(tmp_filename, filename)
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)


class FileWriter(TraceWriter):
    def __init__(self, path: str, *, json: bool = False, html: bool = False):
        if not json and not html:
            raise Exception(
                "At least one output type has to be specified, use json=True or html=True"
            )
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = path
        self.json = json
        self.html = html
        if html:
            self.html_files = copy_static_files(path)

    def write_node_in_progress(self, node: TracingNode):
        self._write_node(node)

    def write_final_node(self, node: TracingNode):
        self._write_node(node)

    def sync(self):
        pass  # DO nothing in this version

    def _write_node(self, node: TracingNode):
        node_as_dict = node.to_dict()
        json_data = json.dumps(node_as_dict)
        if self.json:
            _write_file(os.path.join(self.path, f"trace-{node.uid}.json"), json_data)
        if self.html:
            _write_file(
                os.path.join(self.path, f"trace-{node.uid}.html"),
                get_static_html(json_data, self.html_files),
            )
