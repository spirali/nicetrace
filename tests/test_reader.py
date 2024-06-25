from nicetrace import FileReader, FileWriter, trace


def strip_summary(summary):
    summary = summary.copy()
    start_time = summary.pop("start_time")
    end_time = summary.pop("end_time")
    if summary["state"] == "finished" or summary["state"] == "error":
        assert isinstance(end_time, str)
    else:
        assert end_time is None
    return summary


def test_reader_finished(tmp_path):
    dir = tmp_path / "traces"
    dir.mkdir()
    reader = FileReader(dir)
    assert reader.list_summaries() == []

    with FileWriter(dir):
        with trace("First") as t1:
            pass
        with trace("Second") as t2:
            pass

    s = [strip_summary(x) for x in reader.list_summaries()]
    s.sort(key=lambda x: x["name"])

    assert s == [
        {"uid": t1.uid, "name": "First", "state": "finished"},
        {"uid": t2.uid, "name": "Second", "state": "finished"},
    ]

    assert reader.read_trace(t1.uid) == t1.to_dict()
    assert reader.read_trace(t2.uid) == t2.to_dict()

    t = [strip_summary(x) for x in reader.list_summaries()]
    t.sort(key=lambda x: x["name"])
    assert s == t


def test_reader_running(tmp_path):
    dir = tmp_path / "traces"
    dir.mkdir()
    reader = FileReader(dir)
    assert reader.list_summaries() == []

    with FileWriter(dir) as writer:
        with trace("First") as t1:
            writer.sync()
            with trace("Second"):
                s = [strip_summary(s) for s in reader.list_summaries()]
                assert s == [
                    {"uid": t1.uid, "name": "First", "state": "open"},
                ]
    s = [strip_summary(s) for s in reader.list_summaries()]
    assert len(s) == 1
    assert s[0]["state"] == "finished"
