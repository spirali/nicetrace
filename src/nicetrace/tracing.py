from contextlib import contextmanager
import contextvars
import datetime
import functools
import inspect
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

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

    @staticmethod
    def into_tag(obj: Union[str, "Tag"]) -> "Tag":
        if isinstance(obj, Tag):
            return obj
        if isinstance(obj, str):
            return Tag(obj)
        raise Exception(f"Object {obj!r} cannot be converted into Tag")


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
        meta: Optional[Dict[str, Data]] = None,
        tags: Optional[Sequence[str | Tag]] = None,
        output=None,
        lock=None,
    ):
        """
        - `name` - A description or name for the tracing node.
        - `kind` - Indicates category of the tracing node, may e.g. influence display of the tracing node.
        - `inputs` - A dictionary of inputs for the tracing node.
        - `meta` - A dictionary of any metadata for the tracing node, e.g. UI style data.
        - `tags` - A list of tags for the tracing node
        - `directory` - Whether to create a sub-directory for the tracing node while storing.
          This allows you to split the stored data across multiple files.
        - `output` - The output value of the tracing node, if it has already been computed.
        """

        if inputs:
            assert isinstance(inputs, dict)
            assert all(isinstance(key, str) for key in inputs)
            inputs = serialize_with_type(inputs)

        if meta:
            meta = serialize_with_type(meta)

        if output:
            output = serialize_with_type(output)

        if tags is not None:
            tags = [Tag.into_tag(tag) for tag in tags]

        self.name = name
        self.kind = kind
        self.inputs = inputs
        self.output = output
        self.error = None
        self.state: TracingNodeState = (
            TracingNodeState.OPEN if output is None else TracingNodeState.FINISHED
        )
        self.uid = generate_uid()
        self.children: List[TracingNode] = []
        self.tags: List[Tag] | None = tags
        self.start_time = datetime.datetime.now() if output is None else None
        self.end_time = None if output is None else datetime.datetime.now()
        self.meta = meta
        self._lock = lock
        # self._token = None
        # self._lock = None

    def _to_dict(self):
        result = {"name": self.name, "uid": self.uid}
        if self.state != TracingNodeState.FINISHED:
            result["state"] = self.state.value
        for name in "kind", "output", "error", "tags":
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        if self.inputs:
            result["inputs"] = self.inputs
        if self.children:
            result["children"] = [c._to_dict() for c in self.children]
        if self.start_time:
            result["start_time"] = self.start_time.isoformat()
        if self.end_time:
            result["end_time"] = self.end_time.isoformat()
        if self.meta:
            result["meta"] = self.meta
        if self.tags:
            result["tags"] = serialize_with_type(self.tags)
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
            if self.tags is None:
                self.tags = [Tag.into_tag(tag)]
            else:
                self.tags.append(Tag.into_tag(tag))

    def add_leaf(
        self,
        name: str,
        kind: Optional[str] = None,
        data: Optional[Any] = None,
        meta: Optional[Dict[str, Data]] = None,
        tags: Optional[List[str | Tag]] = None,
    ) -> "TracingNode":
        event = TracingNode(name=name, kind=kind, output=data, meta=meta, tags=tags)
        with self._lock:
            self.children.append(event)
        return event

    def add_meta(self, name: str, value: object):
        """
        Add a named metadata entry

        If an input of the same name already exists, it is overriden
        """
        with self._lock:
            if self.meta is None:
                self.meta = {}
            self.meta[name] = serialize_with_type(value)

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

    def has_tag_name(self, tag_name: str):
        """
        Returns `True` if the tracing node has a tag with the given name.
        """
        if not self.tags:
            return False
        for tag in self.tags:
            if tag == tag_name or (isinstance(tag, Tag) and tag.name == tag_name):
                return True
        return False

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
    tags: Optional[Sequence[str | Tag]] = None,
) -> tuple[TracingNode, Any]:
    parents = _TRACING_STACK.get()
    if parents:
        parent = parents[-1]
        lock = parent._lock
    else:
        parent = None
        lock = Lock()
    node = TracingNode(name, kind, inputs, meta, tags, lock=lock)
    token = _TRACING_STACK.set(parents + (node,))
    writer = get_current_writer()
    if parent:
        with lock:
            assert parent.state == TracingNodeState.OPEN
            parent.children.append(node)
        if writer:
            writer.write_node_in_progress(parent)
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
        node.end_time = datetime.datetime.now()
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
    meta: Optional[Dict[str, Data]] = None,
    tags: Optional[Sequence[str | Tag]] = None,
):
    node, token = start_trace_block(name, kind, inputs, meta, tags)
    try:
        yield node
    except BaseException as e:
        end_trace_block(node, token, e)
        raise e
    end_trace_block(node, token, None)


def with_trace(
    fn: Callable = None, *, name=None, kind=None, tags: Optional[List[str | Tag]] = None
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
                tags=tags,
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
