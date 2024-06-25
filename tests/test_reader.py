from nicetrace import FileReader, FileWriter, trace


def strip_summary(summary):
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

    s = [strip_summary(s) for s in reader.list_summaries()]
    s.sort(key=lambda x: x["name"])

    assert s == [
        {"uid": t1.uid, "name": "First", "state": "finished"},
        {"uid": t2.uid, "name": "Second", "state": "finished"},
    ]

    assert reader.read_serialized_node(t1.uid) == t1.to_dict()
    assert reader.read_serialized_node(t2.uid) == t2.to_dict()


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
    assert s == [
        {"uid": t1.uid, "name": "First", "state": "finished"},
    ]
    t = reader.list_summaries()
    assert s[0] is t[0]
