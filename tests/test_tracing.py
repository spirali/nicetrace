from nicetrace import TracingNodeState, current_tracing_node, trace, with_trace
from nicetrace.tracing import Tag
import pytest
import json
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
            c2.set_output("blabla")
        assert c2.state == TracingNodeState.FINISHED
        with pytest.raises(TestException, match="well"):
            with trace("c2") as c2:
                assert current_tracing_node() is c2
                raise TestException("Ah well")
        assert c2.state == TracingNodeState.ERROR
        assert func1(10, 20) == 30
    assert c.state == TracingNodeState.FINISHED
    print(c.to_dict())
    output = strip_tree(c.to_dict())
    #  print(json.dumps(output, indent=2))
    del output["children"][1]["error"]["traceback"]["frames"][0]
    assert output == {
        "name": "Test",
        "kind": "root",
        "children": [
            {"name": "c1", "output": "blabla"},
            {
                "name": "c2",
                "state": "error",
                "error": {
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
            {
                "name": "func1",
                "kind": "call",
                "inputs": {"param1": 10, "param2": 20},
                "output": 30,
                "children": [
                    {
                        "name": "<lambda>",
                        "kind": "call",
                        "inputs": {"x": "abc"},
                        "output": "abc",
                    },
                    {
                        "name": "myfn",
                        "kind": "call",
                        "inputs": {"x": "abc"},
                        "output": "abc",
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
    del output["error"]["traceback"]["frames"][0]
    assert output == {
        "name": "root",
        "state": "error",
        "error": {
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


def test_tracing_dataclass():
    @dataclass
    class MyData:
        name: str
        age: int

    with trace("root") as c:
        c.add_input("my_input", MyData("Bob", 25))
        c.set_output(MyData("Alice", 26))
    assert c.state == TracingNodeState.FINISHED
    # with_new_context("ch3", lambda d: f"Hello {d.name}", Data(name="LLM"))
    output = strip_tree(c.to_dict())
    assert output == {
        "name": "root",
        "inputs": {"my_input": {"_type": "MyData", "age": 25, "name": "Bob"}},
        "output": {"name": "Alice", "age": 26, "_type": "MyData"},
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
    # print(output)
    assert output == {
        "name": "root",
        "children": [
            {
                "name": "child1",
                "inputs": {"x": 10, "y": {"_type": "A", "id": id(a)}},
            },
            {
                "name": "child1",
                "inputs": {
                    "z": 20,
                    "x": 10,
                    "y": {"_type": "A", "id": id(a)},
                },
            },
        ],
    }


def test_tracing_node_lists():
    with trace("root", inputs={"a": [1, 2, 3]}) as c:
        c.set_output(["A", ["B", "C"]])
    output = strip_tree(c.to_dict())
    print(output)
    assert output == {
        "name": "root",
        "inputs": {"a": [1, 2, 3]},
        "output": ["A", ["B", "C"]],
    }


def test_tracing_node_events():
    with trace("root") as c:
        c.add_leaf("Message to Alice", kind="message", data={"x": 10, "y": 20})
    output = strip_tree(c.to_dict())
    # print(json.dumps(output, indent=2))
    assert output == {
        "name": "root",
        "children": [
            {
                "name": "Message to Alice",
                "kind": "message",
                "output": {"x": 10, "y": 20},
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
    assert output == {
        "name": "root",
        "children": [
            {
                "name": "make_queries",
                "kind": "acall",
                "output": "a",
            },
            {
                "name": "make_queries",
                "kind": "acall",
                "output": "a",
            },
        ],
    }


def test_tracing_node_tags():
    with trace("root", tags=["abc", "xyz"]) as c:
        c.add_tag("123")
        with trace("child"):
            current_tracing_node().add_tag("mmm")
            current_tracing_node().add_tag(Tag("nnn", color="green"))

    data = c.to_dict()
    root = strip_tree(copy.deepcopy(data))
    assert root == {
        "name": "root",
        "tags": [
            {"name": "abc", "color": None, "_type": "Tag"},
            {"name": "xyz", "color": None, "_type": "Tag"},
            {"name": "123", "color": None, "_type": "Tag"},
        ],
        "children": [
            {
                "name": "child",
                "tags": [
                    {"name": "mmm", "color": None, "_type": "Tag"},
                    {"name": "nnn", "color": "green", "_type": "Tag"},
                ],
            }
        ],
    }


def test_find_tracing_nodes():
    with trace("root") as c:
        c.add_tag("123")
        with trace("child"):
            with trace("child3") as c3:
                c3.add_tag("x")
                c3.set_output("abc")
        with trace("child2", tags=[Tag("x")]) as c4:
            pass

    assert c.find_nodes(lambda ctx: ctx.has_tag_name("x")) == [c3, c4]


@pytest.mark.parametrize(
    "output",
    [pytest.param(None, id="None"), pytest.param("", id='""'), 0, 1, "abc", {"x": 10}],
)
def test_to_dict(output):
    with trace("root") as c:
        c.set_output(output)
    assert c.output == output

    c_dict = c.to_dict()
    for key, c_dict_val in c_dict.items():
        if key.startswith("_") or key == "version" or key == "interlab":
            # ignore private attributes or version attributes
            continue
        c_val = getattr(c, key)
        if type(c_val) not in (int, float, str, bool, list, dict, type(None)):
            # only check attributes which are json serializable
            continue
        assert c_dict_val == c_val
