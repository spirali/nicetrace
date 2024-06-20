from contextvars import ContextVar
from abc import ABC, abstractmethod
from typing import Optional

from .tracing import TracingNode

_TRACE_WRITER: ContextVar[Optional["TraceWriter"]] = ContextVar(
    "_TRACE_WRITER", default=None
)


class TraceWriter(ABC):
    @abstractmethod
    def write_node_in_progress(self, node: TracingNode):
        raise NotImplementedError()

    @abstractmethod
    def write_final_node(self, node: TracingNode):
        raise NotImplementedError()

    def __enter__(self):
        self.__token = _TRACE_WRITER.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _TRACE_WRITER.reset(self.__token)


def get_current_writer() -> TraceWriter | None:
    return _TRACE_WRITER.get()
