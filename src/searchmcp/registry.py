import os
from searchmcp.duckduckgo import DuckDuckGoBackend
from searchmcp.brave import BraveBackend
from searchmcp.tavily import TavilyBackend
from searchmcp.bing import BingBackend


def get_backends() -> list[type]:
    backends = [DuckDuckGoBackend]

    if os.environ.get("BRAVE_API_KEY"):
        backends.append(BraveBackend)
    if os.environ.get("TAVILY_API_KEY"):
        backends.append(TavilyBackend)
    if os.environ.get("BING_API_KEY"):
        backends.append(BingBackend)

    return backends
