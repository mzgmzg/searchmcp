from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str

    def __str__(self) -> str:
        return f"[{self.title}]({self.url})\n{self.snippet}"


class SearchBackend(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        ...
