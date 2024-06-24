from contextlib import contextmanager
import contextvars
from datetime import datetime
import functools
import inspect
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

from .utils.ids import generate_uid
from .serialization import Data, serialize_with_type

TRACING_FORMAT_VERSION = "4"

_TRACING_STACK = contextvars.ContextVar("_TRACING_STACK", default=())


class TracingNodeState(Enum):
    """
    An enumeration representing the state of a tracing node.
    """

    OPEN = "open"
    """The tracing node is currently running."""
    FINISHED = "finished"
    """The tracing node has successfully finished execution."""
    ERROR = "error"
    """The tracing node finished with an exception."""


@dataclass
class Tag:
    """
    A simple class representing a tag that can be applied to a tracing node. Optionally with style information.
    """

    name: str
    """The name of the tag; any short string."""
    color: Optional[str] = None
    """HTML color code, e.g. `#ff0000`."""


@dataclass
class Metadata:
    icon: str | None = None
    color: str | None = None
    tags: list[Tag] | None = None
    counters: Dict[str, int] | None = None
    collapse: str | None = None
    custom: Any = None


class TracingNode:
    """
    A tracing object that represents a single request or (sub)task in a nested hierarchy.

    The class has several attributes that are intended as read-only; use setters to modify them.

    The `TracingNode` can be used as context manager, e.g.:

    ```python
    with TracingNode("my node", inputs={"z": 42}) as c:
        c.add_input("x", 1)
        y = do_some_computation(x=1)
        # The tracing node would also note any exceptions raised here
        # (letting it propagate upwards), but an output needs to be set manually:
        c.set_output(y)
    # <- Here the tracing node is already closed.
    ```
    """

    def __init__(
        self,
        name: str,
        kind: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        meta: Optional[Metadata] = None,
        output=None,
        lock=None,
        is_instant=False,
    ):
        """
        - `name` - A description or name for the tracing node.
        - `kind` - Indicates category of the tracing node, may e.g. influence display of the tracing node.
        - `inputs` - A dictionary of inputs for the tracing node.
        - `meta` - A dictionary of any metadata for the tracing node, e.g. UI style data.
          This allows you to split the stored data across multiple files.
        - `output` - The output value of the tracing node, if it has already been computed.
        """

        if inputs:
            assert isinstance(inputs, dict)
            assert all(isinstance(key, str) for key in inputs)
            inputs = serialize_with_type(inputs)

        if meta:
            assert isinstance(meta, Metadata)

        if output:
            output = serialize_with_type(output)

        self.name = name
        self.kind = kind
        self.inputs = inputs
        self.output = output
        self.error = None
        self.uid = generate_uid()
        self.children: List[TracingNode] = []
        if is_instant:
            self.start_time = None
            self.end_time = datetime.now()
            self.state = TracingNodeState.FINISHED
        else:
            self.start_time = datetime.now()
            self.end_time = None
            self.state = TracingNodeState.OPEN
        self.meta = meta
        self._lock = lock

    def _to_dict(self):
        result = {"name": self.name, "uid": self.uid}
        if self.state != TracingNodeState.FINISHED:
            result["state"] = self.state.value
        for name in "kind", "output", "error":
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        if (
            self.inputs
        ):  # We cannot use cycle above, because we want to get rid also empty dict
            result["inputs"] = self.inputs
        if self.children:
            result["children"] = [c._to_dict() for c in self.children]
        if self.start_time:
            result["start_time"] = self.start_time.isoformat()
        if self.end_time:
            result["end_time"] = self.end_time.isoformat()
        if self.meta is not None:
            result["meta"] = serialize_with_type(self.meta)
        return result

    def to_dict(self):
        """
        Serialize `TracingNode` object into JSON structure.
        """
        with self._lock:
            result = self._to_dict()
            result["version"] = TRACING_FORMAT_VERSION
            return result

    def add_tag(self, tag: str | Tag):
        """
        Add a tag to the tracing node.
        """
        with self._lock:
            if self.meta is None:
                self.meta = Metadata()
            if self.meta.tags is None:
                self.meta.tags = []
            self.meta.tags.append(tag)

    def add_instant(
        self,
        name: str,
        kind: Optional[str] = None,
        inputs: Optional[Any] = None,
        output: Optional[Any] = None,
        meta: Optional[Metadata] = None,
    ) -> "TracingNode":
        node = TracingNode(
            name=name,
            kind=kind,
            inputs=inputs,
            output=output,
            meta=meta,
            is_instant=True,
        )
        with self._lock:
            self.children.append(node)
        return node

    def add_input(self, name: str, value: object):
        """
        Add a named input value to the tracing node.

        If an input of the same name already exists, an exception is raised.
        """
        with self._lock:
            if self.inputs is None:
                self.inputs = {}
            if name in self.inputs:
                raise Exception(f"Input {name} already exists")
            self.inputs[name] = serialize_with_type(value)

    def add_inputs(self, inputs: dict[str, object]):
        """
        Add a new input values to the tracing node.

        If an input of the same name already exists, an exception is raised.
        """
        with self._lock:
            if self.inputs is None:
                self.inputs = {}
            for name in inputs:
                if name in self.inputs:
                    raise Exception(f"Input {name} already exists")
            for name, value in inputs.items():
                self.inputs[name] = serialize_with_type(value)

    def set_output(self, value: Any):
        """
        Set the output value of the tracing node.
        """
        with self._lock:
            self.output = serialize_with_type(value)

    def set_error(self, exc: Any):
        """
        Set the error value of the tracing node (usually an `Exception` instance).
        """
        with self._lock:
            self.state = TracingNodeState.ERROR
            self.error = serialize_with_type(exc)

    def find_nodes(self, predicate: Callable) -> List["TracingNode"]:
        """
        Find all nodes matching the given callable `predicate`.

        The predicate is called with a single argument, the `TracingNode` to check, and should return `bool`.
        """

        def _helper(node: TracingNode):
            if predicate(node):
                result.append(node)
            if node.children:
                for child in node.children:
                    _helper(child)

        result = []
        with self._lock:
            _helper(self)
        return result

    # def write_html(self, filename: str):
    #     from ..ui.staticview import create_node_static_page

    #     html = create_node_static_page(self)
    #     with open(filename, "w") as f:
    #         f.write(html)

    # def display(self):
    #     """Show tracing in Jupyter notebook"""
    #     from IPython.core.display import HTML
    #     from IPython.display import display

    #     from ..ui.staticview import create_node_static_html

    #     html = create_node_static_html(self)
    #     display(HTML(html))


def start_trace_block(
    name: str,
    kind: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    meta: Optional[Dict[str, Data]] = None,
) -> tuple[TracingNode, Any]:
    parents = _TRACING_STACK.get()
    if parents:
        parent = parents[-1]
        lock = parent._lock
    else:
        parent = None
        lock = Lock()
    node = TracingNode(name, kind, inputs, meta, lock=lock)
    token = _TRACING_STACK.set(parents + (node,))
    writer = get_current_writer()
    if parent:
        with lock:
            assert parent.state == TracingNodeState.OPEN
            parent.children.append(node)
        if writer:
            writer.write_node_in_progress(parents[0])
    else:
        if writer:
            writer.write_node_in_progress(node)
    return node, token


def end_trace_block(node, token, error):
    _TRACING_STACK.reset(token)
    with node._lock:
        if node.state == TracingNodeState.OPEN:
            if error is None:
                node.state = TracingNodeState.FINISHED
            else:
                node.state = TracingNodeState.ERROR
                node.error = serialize_with_type(error)
        node.end_time = datetime.now()
    writer = get_current_writer()
    if writer:
        parents = _TRACING_STACK.get()
        if parents:
            writer.write_node_in_progress(parents[0])
        else:
            writer.write_final_node(node)


@contextmanager
def trace(
    name: str,
    kind: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    meta: Optional[Metadata] = None,
):
    node, token = start_trace_block(name, kind, inputs, meta)
    try:
        yield node
    except BaseException as e:
        end_trace_block(node, token, e)
        raise e
    end_trace_block(node, token, None)


def trace_instant(
    name: str,
    kind: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    output: Optional[Any] = None,
    meta: Optional[Metadata] = None,
):
    return current_tracing_node().add_instant(name, kind, inputs, output, meta)


def with_trace(
    fn: Callable = None, *, name=None, kind=None, meta: Optional[Metadata] = None
):
    """
    A decorator wrapping every execution of the function in a new `TracingNode`.

    The `inputs`, `output`, and `error` (if any) are set automatically.
    Note that you can access the created tracing in your function using `current_tracing_node`.

    *Usage:*

    ```python
    @with_trace
    def func():
        pass

    @with_trace(name="custom_name", kind="custom_kind", tags=['tag1', 'tag2'])
    def func():
        pass
    ```
    """
    if isinstance(fn, str):
        raise TypeError("use `with_tracing()` with explicit `name=...` parameter")

    def helper(func):
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*a, **kw):
            binding = signature.bind(*a, **kw)
            with trace(
                name=name or func.__name__,
                kind=kind or "call",
                inputs=binding.arguments,
                meta=meta,
            ) as node:
                output = func(*a, **kw)
                node.set_output(output)
                return output

        async def async_wrapper(*a, **kw):
            binding = signature.bind(*a, **kw)
            with trace(
                name=name or func.__name__,
                kind=kind or "acall",
                inputs=binding.arguments,
            ) as node:
                output = await func(*a, **kw)
                node.set_output(output)
                return output

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    if fn is not None:
        assert callable(fn)
        return helper(fn)
    else:
        return helper


def current_tracing_node(check: bool = True) -> Optional[TracingNode]:
    """
    Returns the inner-most open tracing node, if any.

    Throws an error if `check` is `True` and there is no current tracing node. If `check` is `False` and there is
    no current tracing node, it returns `None`.
    """
    stack = _TRACING_STACK.get()
    if not stack:
        if check:
            raise Exception("No current tracing")
        return None
    return stack[-1]


from .writer import get_current_writer
