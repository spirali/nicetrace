from nicetrace.tracing import TRACING_FORMAT_VERSION


def strip_tree(obj, erase_error_details=False, root=True):
    if isinstance(obj, dict):
        if "uid" in obj:
            assert isinstance(obj.pop("uid"), str)
            if "start_time" in obj:
                assert isinstance(obj.pop("start_time"), str)
            if "end_time" in obj:
                assert isinstance(obj.pop("end_time"), str)
            if root:
                assert obj.pop("version") == TRACING_FORMAT_VERSION

        t = obj.get("_type")
        if t == "$traceback":
            if erase_error_details:
                obj.pop("frames")
            else:
                for frame in obj.get("frames", []):
                    assert isinstance(frame.pop("lineno"), int)
        return {
            key: strip_tree(value, erase_error_details, root=False)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [strip_tree(o, erase_error_details, root=False) for o in obj]
    return obj
