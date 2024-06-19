from nicetrace import get_current_writer, FileWriter
from nicetrace import trace
import json


def test_writer_contextvar(tmp_path):
    assert get_current_writer() is None
    with FileWriter(tmp_path / "one", json=True) as w1:
        assert get_current_writer() is w1
        with FileWriter(tmp_path / "two", html=True) as w2:
            assert get_current_writer() is w2
        assert get_current_writer() is w1
    assert get_current_writer() is None


def test_file_writer(tmp_path):
    dir = tmp_path / "files"

    def read(node):
        with open(dir / f"trace-{node.uid}.json") as f:
            return json.loads(f.read())

    with FileWriter(dir, json=True) as storage:
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
