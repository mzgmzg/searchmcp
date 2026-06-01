from searchmcp.config import Config
from searchmcp.duckduckgo import DuckDuckGoBackend
from searchmcp.brave import BraveBackend
from searchmcp.tavily import TavilyBackend
from searchmcp.bing import BingBackend
from searchmcp.base import SearchBackend


def get_backends(cfg: Config) -> list[SearchBackend]:
    backends = [DuckDuckGoBackend(proxy=cfg.proxy)]

    if cfg.brave_api_key:
        backends.append(BraveBackend(api_key=cfg.brave_api_key, proxy=cfg.proxy))
    if cfg.tavily_api_key:
        backends.append(TavilyBackend(api_key=cfg.tavily_api_key, proxy=cfg.proxy))
    if cfg.bing_api_key:
        backends.append(BingBackend(api_key=cfg.bing_api_key, proxy=cfg.proxy))

    return backends
