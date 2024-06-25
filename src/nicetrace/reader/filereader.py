from .base import TraceReader
import os
import json


class FileReader(TraceReader):
    def __init__(self, path: str):
        if not os.path.isdir(path):
            raise Exception(f"Path '{path}' does not exists")
        self.path = path
        self.finished_paths = {}

    def list_summaries(self) -> list[dict]:
        summaries = []
        finished_paths = self.finished_paths
        for filename in os.listdir(self.path):
            if filename.endswith(".json"):
                summary = finished_paths.get(filename)
                if summary:
                    summaries.append(summary)
                with open(os.path.join(self.path, filename)) as f:
                    snode = json.loads(f.read())
                    state = snode.get("state", "finished")
                    summary = {
                        "uid": snode["uid"],
                        "name": snode["name"],
                        "state": state,
                        "end_time": snode.get("end_time"),
                    }
                    if state != "open":
                        finished_paths[filename] = summary
                    summaries.append(summary)
        return summaries

    def read_serialized_node(self, uid: str) -> dict:
        with open(os.path.join(self.path, f"trace-{uid}.json")) as f:
            return json.loads(f.read())
