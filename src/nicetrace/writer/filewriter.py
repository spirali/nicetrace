from abc import abstractmethod
from threading import Lock, Thread, Condition
from .base import TraceWriter
from ..tracing import TracingNode
from datetime import datetime, timedelta
import time
import uuid
import os
import json
from pathlib import Path


def write_file(filename: str | os.PathLike, data: str):
    tmp_filename = f".{uuid.uuid4().hex}._tmp"
    try:
        with open(tmp_filename, "w") as f:
            f.write(data)
        os.rename(tmp_filename, filename)
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)


def _delay_write_thread(writer):
    with writer.lock:
        sleep_time = writer.min_write_delay.total_seconds()

    while True:
        time.sleep(sleep_time)
        with writer.lock:
            writer._sync()
            writer.condition.wait()
            if writer.state != "running":
                return


class DelayedWriter(TraceWriter):
    def __init__(self, min_write_delay: timedelta):
        self.lock = Lock()
        self.last_write = {}
        self.pending = set()
        self.state = "new"
        self.min_write_delay = min_write_delay
        self.condition = Condition(self.lock)
        self.thread = Thread(target=_delay_write_thread, args=(self,), daemon=True)

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

    def _write_node(self, node: TracingNode, final: bool):
        uid = node.uid
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

    @abstractmethod
    def _write_node_to_file(self, node):
        pass


class DirWriter(DelayedWriter):
    """
    Writes JSON serialized trace into a given directory.
    Trace is saved under filename trace-<ID>.json.
    It allows to write multiple traces at once.
    """

    def __init__(
        self, path: str, min_write_delay: timedelta = timedelta(milliseconds=300)
    ):
        super().__init__(min_write_delay)
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = path

    def _write_node_to_file(self, node):
        json_data = json.dumps(node.to_dict())
        write_file(os.path.join(self.path, f"trace-{node.uid}.json"), json_data)

    def write_node(self, node: TracingNode, final: bool):
        with self.lock:
            self._write_node(node, final)


class FileWriter(DelayedWriter):
    """
    Write JSON serialized trace into given file.
    It allows to write only one trace at time.
    It throws an error if more then one top-level trace node is created at once.
    """

    def __init__(
        self, filename: str, min_write_delay: timedelta = timedelta(milliseconds=300)
    ):
        super().__init__(min_write_delay)

        filename = os.path.abspath(filename)
        path = os.path.dirname(filename)
        Path(path).mkdir(parents=True, exist_ok=True)
        if not filename.endswith(".json"):
            filename = filename + ".json"

        self.filename = filename
        self.current_node = None

    def _write_node_to_file(self, node):
        json_data = json.dumps(node.to_dict())
        write_file(self.filename, json_data)

    def write_node(self, node: TracingNode, final: bool):
        with self.lock:
            if self.current_node is None:
                self.current_node = node
            elif node != self.current_node:
                raise Exception(
                    "FileWriter allows to write only one root node at once,"
                    "use DirWriter if you need "
                )
            self._write_node(node, final)
            if final:
                self.current_node = None
