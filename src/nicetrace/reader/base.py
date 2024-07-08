from abc import ABC, abstractmethod


class TraceReader(ABC):
    """Abstract base class for reading traces"""

    @abstractmethod
    def list_summaries(self) -> list[dict]:
        """Get summaries of traces in storage"""
        raise NotImplementedError()

    @abstractmethod
    def read_trace(self, uid: str) -> dict:
        """Read a trace from storage"""
        raise NotImplementedError()
