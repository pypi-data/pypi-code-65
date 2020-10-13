from abc import ABC, abstractmethod


class QuerySequence(ABC):

    query_execution_order = None
    client = None
    queries = None

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def setup_query_context(self, query_context: dict) -> None:
        pass

    def parse_execution_order(self) -> None:
        self.query_execution_order = sorted(
            [int(string_index) for string_index in list(self.queries.keys())]
        )
