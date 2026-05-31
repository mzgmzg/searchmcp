import asyncio
from searchmcp.base import SearchBackend, SearchResult


class DuckDuckGoBackend(SearchBackend):
    name = "duckduckgo"
    description = "Search the web using DuckDuckGo. Free, no API key required."

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        from ddgs import DDGS

        raw = await asyncio.to_thread(
            lambda: DDGS().text(query, max_results=max_results)
        )

        results = []
        for r in raw:
            results.append(SearchResult(
                title=r.get("title", ""),
                url=r.get("href", ""),
                snippet=r.get("body", ""),
            ))
        return results
