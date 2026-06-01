import httpx
from searchmcp.base import SearchBackend, SearchResult


class BraveBackend(SearchBackend):
    name = "brave"
    description = "Search the web using Brave Search API. Set BRAVE_API_KEY to activate."

    def __init__(self, api_key: str = "", proxy: str = ""):
        self.api_key = api_key
        self.proxy = proxy

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        params = {"q": query, "count": min(max_results, 20)}

        async with httpx.AsyncClient(proxy=self.proxy or None) as client:
            resp = await client.get(url, headers=headers, params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for r in data.get("web", {}).get("results", []):
            results.append(SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("description", ""),
            ))
        return results
