import httpx
from searchmcp.base import SearchBackend, SearchResult


class TavilyBackend(SearchBackend):
    name = "tavily"
    description = "Search the web using Tavily Search API. Set TAVILY_API_KEY to activate."

    def __init__(self, api_key: str = "", proxy: str = ""):
        self.api_key = api_key
        self.proxy = proxy

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        url = "https://api.tavily.com/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "search_depth": "basic",
            "topic": "general",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        async with httpx.AsyncClient(proxy=self.proxy or None) as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for r in data.get("results", []):
            results.append(SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("content", ""),
            ))
        return results
