import httpx
from searchmcp.base import SearchBackend, SearchResult


class SearXNGBackend(SearchBackend):
    name = "searxng"
    description = "搜索网页，通过自部署的 SearXNG 元搜索引擎。设置 SEARXNG_BASE_URL 激活。"

    def __init__(self, base_url: str = "", proxy: str = ""):
        self.base_url = base_url.rstrip("/")
        self.proxy = proxy

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        url = f"{self.base_url}/search"
        params = {"q": query, "format": "json"}

        async with httpx.AsyncClient(proxy=self.proxy or None) as client:
            resp = await client.get(url, params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for r in data.get("results", [])[:max_results]:
            results.append(SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("content", ""),
            ))
        return results
