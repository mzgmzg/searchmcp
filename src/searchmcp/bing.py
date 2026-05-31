import os
import httpx
from searchmcp.base import SearchBackend, SearchResult


class BingBackend(SearchBackend):
    name = "bing"
    description = "Search the web using Bing Web Search API. Set BING_API_KEY to activate."

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        api_key = os.environ["BING_API_KEY"]
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {"q": query, "count": max_results}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for r in data.get("webPages", {}).get("value", []):
            results.append(SearchResult(
                title=r.get("name", ""),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
            ))
        return results
