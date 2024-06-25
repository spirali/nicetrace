from abc import ABC, abstractmethod


class TraceReader(ABC):
    @abstractmethod
    def list_summaries(self) -> list[dict]:
        raise NotImplementedError()

    @abstractmethod
    def read_serialized_node(self, uid: str) -> dict:
        raise NotImplementedError()
