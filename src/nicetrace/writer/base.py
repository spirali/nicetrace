from contextvars import ContextVar
from abc import ABC, abstractmethod
from typing import Optional

from ..tracing import TracingNode

_TRACE_WRITER: ContextVar[Optional["TraceWriter"]] = ContextVar(
    "_TRACE_WRITER", default=None
)


class TraceWriter(ABC):
    """
    Abstract base class for all trace writers.
    """

    @abstractmethod
    def write_node(self, node: TracingNode, final: bool):
        raise NotImplementedError()

    @abstractmethod
    def sync(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def __enter__(self):
        self.__token = _TRACE_WRITER.set(self)
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        _TRACE_WRITER.reset(self.__token)


def current_writer() -> TraceWriter | None:
    """
    Get the current global writer.
    """
    return _TRACE_WRITER.get()
