from nicetrace import TracingNodeState, current_tracing_node, trace, with_trace
from nicetrace import Tag, Metadata
from nicetrace import trace_instant
import pytest
import copy
from dataclasses import dataclass


from testutils import strip_tree


def test_tracing_node_basic():
    class TestException(Exception):
        pass

    @with_trace
    def func1(param1, param2):
        assert with_trace(lambda x: x)("abc") == "abc"
        assert with_trace(lambda x: x, name="myfn")("abc") == "abc"
        return param1 + param2

    assert current_tracing_node(check=False) is None
    with trace("Test", kind="root") as c:
        assert c.state == TracingNodeState.OPEN
        assert current_tracing_node() is c
        with trace("c1") as c2:
            c2.add_output("", "blabla")
        assert c2.state == TracingNodeState.FINISHED
        with pytest.raises(TestException, match="well"):
            with trace("c2") as c2:
                assert current_tracing_node() is c2
                raise TestException("Ah well")
        assert c2.state == TracingNodeState.ERROR
        assert func1(10, 20) == 30
    assert c.state == TracingNodeState.FINISHED
    output = strip_tree(c.to_dict())
    import json

    print(json.dumps(output, indent=2))
    del output["children"][1]["entries"][-1]["value"]["traceback"]["frames"][0]
    assert output == {
        "name": "Test",
        "kind": "root",
        "children": [
            {
                "name": "c1",
                "entries": [{"kind": "output", "value": "blabla"}],
            },
            {
                "name": "c2",
                "state": "error",
                "entries": [
                    {
                        "kind": "error",
                        "value": {
                            "_type": "TestException",
                            "message": "Ah well",
                            "traceback": {
                                "_type": "$traceback",
                                "frames": [
                                    {
                                        "name": "test_tracing_node_basic",
                                        "filename": __file__,
                                        "line": 'raise TestException("Ah well")',
                                    },
                                ],
                            },
                        },
                    },
                ],
            },
            {
                "name": "func1",
                "kind": "call",
                "entries": [
                    {"kind": "input", "name": "param1", "value": 10},
                    {"kind": "input", "name": "param2", "value": 20},
                    {"kind": "output", "value": 30},
                ],
                "children": [
                    {
                        "name": "<lambda>",
                        "kind": "call",
                        "entries": [
                            {"kind": "input", "name": "x", "value": "abc"},
                            {"kind": "output", "value": "abc"},
                        ],
                    },
                    {
                        "name": "myfn",
                        "kind": "call",
                        "entries": [
                            {"kind": "input", "name": "x", "value": "abc"},
                            {"kind": "output", "value": "abc"},
                        ],
                    },
                ],
            },
        ],
    }


def test_tracing_node_inner_exception():
    def f1():
        raise Exception("Exception 1")

    def f2():
        try:
            f1()
        except Exception:
            raise Exception("Exception 2")

    with pytest.raises(Exception):
        with trace("root") as c:
            f2()

    output = strip_tree(c.to_dict())
    # print(json.dumps(output, indent=2))
    del output["entries"][-1]["value"]["traceback"]["frames"][0]
    assert output == {
        "name": "root",
        "state": "error",
        "entries": [
            {
                "kind": "error",
                "value": {
                    "_type": "Exception",
                    "message": "Exception 2",
                    "traceback": {
                        "_type": "$traceback",
                        "frames": [
                            {
                                "name": "test_tracing_node_inner_exception",
                                "filename": __file__,
                                "line": "f2()",
                            },
                            {
                                "name": "f2",
                                "filename": __file__,
                                "line": 'raise Exception("Exception 2")',
                            },
                        ],
                    },
                    "tracing": {
                        "_type": "Exception",
                        "message": "Exception 1",
                        "traceback": {
                            "_type": "$traceback",
                            "frames": [
                                {
                                    "name": "f2",
                                    "filename": __file__,
                                    "line": "f1()",
                                },
                                {
                                    "name": "f1",
                                    "filename": __file__,
                                    "line": 'raise Exception("Exception 1")',
                                },
                            ],
                        },
                    },
                },
            }
        ],
    }


def test_tracing_dataclass():
    @dataclass
    class MyData:
        name: str
        age: int

    with trace("root") as c:
        c.add_input("my_input", MyData("Bob", 25))
        c.add_output("", MyData("Alice", 26))
    assert c.state == TracingNodeState.FINISHED
    # with_new_context("ch3", lambda d: f"Hello {d.name}", Data(name="LLM"))
    output = strip_tree(c.to_dict())
    assert output == {
        "name": "root",
        "entries": [
            {
                "kind": "input",
                "name": "my_input",
                "value": {"_type": "MyData", "age": 25, "name": "Bob"},
            },
            {
                "kind": "output",
                "value": {"name": "Alice", "age": 26, "_type": "MyData"},
            },
        ],
    }


def test_tracing_node_add_inputs():
    class A:
        pass

    a = A()

    with trace("root") as c:
        with trace("child1") as c2:
            c2.add_inputs({"x": 10, "y": a})
        with trace("child1", inputs={"z": 20}) as c2:
            c2.add_inputs({"x": 10, "y": a})
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "name": "root",
        "children": [
            {
                "name": "child1",
                "entries": [
                    {"kind": "input", "value": 10, "name": "x"},
                    {
                        "kind": "input",
                        "value": {"_type": "A", "id": id(a)},
                        "name": "y",
                    },
                ],
            },
            {
                "name": "child1",
                "entries": [
                    {"kind": "input", "value": 20, "name": "z"},
                    {"kind": "input", "value": 10, "name": "x"},
                    {
                        "kind": "input",
                        "value": {"_type": "A", "id": id(a)},
                        "name": "y",
                    },
                ],
            },
        ],
    }


def test_tracing_node_lists():
    with trace("root", inputs={"a": [1, 2, 3]}) as c:
        c.add_output("", ["A", ["B", "C"]])
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "name": "root",
        "entries": [
            {"kind": "input", "value": [1, 2, 3], "name": "a"},
            {"kind": "output", "value": ["A", ["B", "C"]]},
        ],
    }


def test_tracing_node_instants():
    with trace("root") as c:
        trace_instant("Message to Alice", kind="message", inputs={"x": 10, "y": 20})
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "name": "root",
        "children": [
            {
                "name": "Message to Alice",
                "kind": "message",
                "entries": [
                    {"kind": "input", "value": 10, "name": "x"},
                    {"kind": "input", "value": 20, "name": "y"},
                ],
            }
        ],
    }


@pytest.mark.asyncio
async def test_async_tracing_node():
    @with_trace
    async def make_queries():
        return "a"

    with trace("root") as c:
        q1 = make_queries()
        q2 = make_queries()

        await q1
        await q2

    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "name": "root",
        "children": [
            {
                "name": "make_queries",
                "kind": "acall",
                "entries": [{"kind": "output", "value": "a"}],
            },
            {
                "name": "make_queries",
                "kind": "acall",
                "entries": [{"kind": "output", "value": "a"}],
            },
        ],
    }


def test_tracing_node_tags():
    with trace("root", meta=Metadata(tags=[Tag("abc"), Tag("xyz")])) as c:
        c.add_tag(Tag("123"))
        with trace("child"):
            current_tracing_node().add_tag(Tag("mmm"))
            current_tracing_node().add_tag(Tag("nnn", color="green"))

    data = c.to_dict()
    root = strip_tree(copy.deepcopy(data))
    assert root["meta"]["tags"] == [
        {"name": "abc", "_type": "Tag"},
        {"name": "xyz", "_type": "Tag"},
        {"name": "123", "_type": "Tag"},
    ]
    assert root["children"][0]["meta"]["tags"] == [
        {"name": "mmm", "_type": "Tag"},
        {"name": "nnn", "color": "green", "_type": "Tag"},
    ]


@pytest.mark.parametrize(
    "output",
    [pytest.param(None, id="None"), pytest.param("", id='""'), 0, 1, "abc", {"x": 10}],
)
def test_to_dict(output):
    with trace("root") as c:
        c.add_output("", output)
    c_dict = c.to_dict()
    for key, c_dict_val in c_dict.items():
        if key.startswith("_") or key == "version":
            # ignore private attributes or version attributes
            continue
        c_val = getattr(c, key)
        if type(c_val) not in (int, float, str, bool, list, dict, type(None)):
            # only check attributes which are json serializable
            continue
        assert c_dict_val == c_val
