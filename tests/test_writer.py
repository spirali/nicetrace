from nicetrace import current_writer, DirWriter, FileWriter
from nicetrace import trace
import json
import time


def test_writer_contextvar(tmp_path):
    assert current_writer() is None
    with DirWriter(tmp_path / "one") as w1:
        assert current_writer() is w1
        with DirWriter(tmp_path / "two") as w2:
            assert current_writer() is w2
        assert current_writer() is w1
    assert current_writer() is None


def test_dir_writer_json_delayed(tmp_path):
    dir = tmp_path / "traces"

    def read(node):
        with open(dir / f"trace-{node.uid}.json") as f:
            return json.loads(f.read())

    with DirWriter(dir):
        with trace("Hello") as node:
            with trace("Xyxy"):
                pass
            assert "children" not in read(node)
            time.sleep(1)
            data = read(node)
            assert len(data["children"]) == 1
            assert data["children"][0]["name"] == "Xyxy"


def test_dir_writer_json(tmp_path):
    dir = tmp_path / "traces"

    def read(node):
        with open(dir / f"trace-{node.uid}.json") as f:
            return json.loads(f.read())

    with DirWriter(dir) as storage:
        with trace("Hello") as node:
            storage.sync()
            data = read(node)
            assert data["name"] == "Hello"
            assert data["state"] == "open"
            assert "children" not in data

            with trace("First child"):
                storage.sync()
                data = read(node)
                assert data["name"] == "Hello"
                assert data["state"] == "open"
                assert data["children"][0]["name"] == "First child"
                assert data["children"][0]["state"] == "open"

            storage.sync()
            data = read(node)
            assert data["name"] == "Hello"
            assert data["state"] == "open"
            assert data["children"][0]["name"] == "First child"
            assert "state" not in data["children"][0]

        storage.sync()
        data = read(node)
        assert data["name"] == "Hello"
        assert "state" not in data
        assert data["children"][0]["name"] == "First child"
        assert "state" not in data["children"][0]


def test_file_writer(tmp_path):
    path = tmp_path / "traces" / "my.json"

    def read():
        with open(path) as f:
            return json.loads(f.read())

    writer = FileWriter(path)
    with trace("Root", writer=writer):
        assert read()["state"] == "open"
    data = read()
    assert "state" not in data
    with trace("Root", writer=writer):
        assert read()["state"] == "open"
    data2 = read()
    assert "state" not in data2
    assert data["uid"] != data2["uid"]
