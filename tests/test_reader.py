from nicetrace import DirReader, DirWriter, trace, FileWriter


def strip_summary(summary):
    summary = summary.copy()
    start_time = summary.pop("start_time")
    assert isinstance(start_time, str)
    end_time = summary.pop("end_time")
    if summary["state"] == "finished" or summary["state"] == "error":
        assert isinstance(end_time, str)
    else:
        assert end_time is None
    return summary


def test_reader_finished(tmp_path):
    dir = tmp_path / "traces"
    dir.mkdir()
    reader = DirReader(dir)
    assert reader.list_summaries() == []

    with DirWriter(dir):
        with trace("First") as t1:
            pass
        with trace("Second") as t2:
            pass
    with FileWriter(dir / "hello1"):
        with trace("Hello") as t3:
            pass

    s = {x["storage_id"]: strip_summary(x) for x in reader.list_summaries()}
    assert s == {
        f"trace-{t1.uid}": {
            "storage_id": f"trace-{t1.uid}",
            "uid": t1.uid,
            "name": "First",
            "state": "finished",
        },
        f"trace-{t2.uid}": {
            "storage_id": f"trace-{t2.uid}",
            "uid": t2.uid,
            "name": "Second",
            "state": "finished",
        },
        "hello1": {
            "storage_id": "hello1",
            "uid": t3.uid,
            "name": "Hello",
            "state": "finished",
        },
    }

    assert reader.read_trace(f"trace-{t1.uid}") == t1.to_dict()
    assert reader.read_trace(f"trace-{t2.uid}") == t2.to_dict()
    assert reader.read_trace("hello1") == t3.to_dict()

    t = {x["storage_id"]: strip_summary(x) for x in reader.list_summaries()}
    assert s == t


def test_reader_running(tmp_path):
    dir = tmp_path / "traces"
    dir.mkdir()
    reader = DirReader(dir)
    assert reader.list_summaries() == []

    with DirWriter(dir) as writer:
        with trace("First") as t1:
            writer.sync()
            with trace("Second"):
                s = [strip_summary(s) for s in reader.list_summaries()]
                assert s == [
                    {
                        "storage_id": f"trace-{t1.uid}",
                        "uid": t1.uid,
                        "name": "First",
                        "state": "open",
                    },
                ]
    s = [strip_summary(s) for s in reader.list_summaries()]
    assert len(s) == 1
    assert s[0]["state"] == "finished"
