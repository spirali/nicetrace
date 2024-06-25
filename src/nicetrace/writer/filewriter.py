from abc import abstractmethod
from threading import Lock, Thread, Condition
from ..html.statichtml import get_static_html
from ..html.staticfiles import copy_static_files
from .base import TraceWriter
from ..tracing import TracingNode
from datetime import datetime, timedelta
import time
import uuid
import os
import json
from pathlib import Path


def _write_file(filename: str, data: str):
    tmp_filename = f".{uuid.uuid4().hex}._tmp"
    try:
        with open(tmp_filename, "w") as f:
            f.write(data)
        os.rename(tmp_filename, filename)
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)


def _deplay_write_thread(writer):
    with writer.lock:
        sleep_time = writer.min_write_delay.total_seconds()

    while True:
        time.sleep(sleep_time)
        with writer.lock:
            writer._sync()
            writer.condition.wait()
            if writer.state != "running":
                return


class FileWriter(TraceWriter):
    def __init__(
        self, path: str, min_write_delay: timedelta = timedelta(milliseconds=300)
    ):
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = path
        self.lock = Lock()
        self.last_write = {}
        self.pending = set()
        self.state = "new"
        self.min_write_delay = min_write_delay
        self.condition = Condition(self.lock)
        self.thread = Thread(target=_deplay_write_thread, args=(self,), daemon=True)

        # self.json = json
        # self.html = html
        # if html:
        #     self.html_files = copy_static_files(path)

    def start(self):
        with self.lock:
            assert self.state == "new"
            self.state = "running"
            self.thread.start()

    def stop(self):
        with self.lock:
            self._sync()
            self.state = "stopped"
            self.condition.notify()

    def write_node(self, node: TracingNode, final: bool):
        uid = node.uid
        with self.lock:
            if final:
                self._write_node_to_file(node)
                self.last_write.pop(uid, None)
                if node in self.pending:
                    self.pending.remove(node)
            else:
                last_write = self.last_write.get(uid)
                now = datetime.now()
                if last_write and now - last_write < self.min_write_delay:
                    self.pending.add(node)
                    self.condition.notify()
                else:
                    self._write_node_to_file(node)
                    self.last_write[uid] = now

    def _sync(self):
        for node in self.pending:
            self._write_node_to_file(node)
            self.last_write[node.uid] = datetime.now()
        self.pending.clear()

    def sync(self):
        with self.lock:
            self._sync()

    def _write_node_to_file(self, node):
        json_data = json.dumps(node.to_dict())
        _write_file(os.path.join(self.path, f"trace-{node.uid}.json"), json_data)

    # def _write_node(self, node: TracingNode):
    #     node_as_dict = node.to_dict()
    #     json_data = json.dumps(node_as_dict)
    #     if self.json:
    #         _write_file(os.path.join(self.path, f"trace-{node.uid}.json"), json_data)
    #     if self.html:
    #         _write_file(
    #             os.path.join(self.path, f"trace-{node.uid}.html"),
    #             get_static_html(json_data, self.html_files),
    #         )
