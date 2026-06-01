import argparse
import re
import logging
import httpx
import anyio
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from searchmcp.config import Config, load_config
from searchmcp.registry import get_backends
from searchmcp.base import SearchBackend

logger = logging.getLogger(__name__)

mcp = FastMCP("searchmcp")

_FETCH_TIMEOUT = 30.0
_FETCH_MAX_BYTES = 1024 * 1024  # 1MB

_api_key_required_paths = ("/sse", "/messages")


def _html_to_text(html: str) -> str:
    stripped = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    stripped = re.sub(r"<style[^>]*>.*?</style>", "", stripped, flags=re.DOTALL | re.IGNORECASE)
    stripped = re.sub(r"<[^>]+>", "", stripped)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    stripped = re.sub(r"[ \t]{2,}", " ", stripped)
    return stripped.strip()


def _format_results(results: list) -> str:
    if not results:
        return "No results found."

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"{i}. [{r.title}]({r.url})\n   {r.snippet}")
    return "\n\n".join(parts)


def _make_handler(backend: SearchBackend):
    async def search(query: str, max_results: int = 10) -> str:
        try:
            results = await backend.search(query, max_results)
            return _format_results(results)
        except Exception as e:
            logger.warning("Backend '%s' failed: %s", backend.name, e)
            return f"Search via {backend.name} failed: {e}"

    search.__name__ = f"search_{backend.name}"
    return search


_BACKENDS: list[SearchBackend] = []


def _make_fetch_handler(proxy: str = ""):
    async def fetch(url: str) -> str:
        """抓取指定 URL 的网页内容，返回纯文本"""
        try:
            async with httpx.AsyncClient(
                timeout=_FETCH_TIMEOUT,
                headers={"User-Agent": "SearchMCP/0.1"},
                follow_redirects=True,
                proxy=proxy or None,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()

                content_type = resp.headers.get("content-type", "")
                if "text/html" in content_type:
                    text = _html_to_text(resp.text)
                else:
                    text = resp.text

                if len(text) > _FETCH_MAX_BYTES:
                    text = text[:_FETCH_MAX_BYTES] + "\n\n[内容已截断...]"

                return text or "[页面内容为空]"

        except httpx.HTTPStatusError as e:
            return f"HTTP 错误: {e.response.status_code}"
        except Exception as e:
            logger.warning("Fetch 失败: %s", e)
            return f"抓取失败: {e}"

    fetch.__name__ = "fetch"
    return fetch


def init(cfg: Config):
    for backend in get_backends(cfg):
        handler = _make_handler(backend)
        mcp.tool(
            name=f"search_{backend.name}",
            description=backend.description,
        )(handler)
        _BACKENDS.append(backend)
        logger.info("Registered tool: search_%s", backend.name)

    fetch_handler = _make_fetch_handler(proxy=cfg.proxy)
    mcp.tool(
        name="fetch",
        description="抓取指定 URL 的网页内容，返回纯文本",
    )(fetch_handler)
    logger.info("Registered tool: fetch")


@mcp.resource("config://backends")
def get_active_backends() -> str:
    names = [b.name for b in _BACKENDS]
    return f"Active search backends: {', '.join(names)}"


class _AuthMiddleware:
    """简易 API Key 鉴权中间件，检查 Authorization: Bearer <key> 头"""

    def __init__(self, app, api_key: str):
        self.app = app
        self.api_key = api_key

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        needs_auth = any(path.startswith(p) for p in _api_key_required_paths)

        if not needs_auth:
            await self.app(scope, receive, send)
            return

        auth_header = dict(scope.get("headers", [])).get(b"authorization", b"").decode()
        expected = f"Bearer {self.api_key}"

        if auth_header == expected:
            await self.app(scope, receive, send)
            return

        response = JSONResponse(
            {"error": "unauthorized", "message": "无效或缺失的 API Key"},
            status_code=401,
        )
        await response(scope, receive, send)


def _run_http(cfg: Config):
    """以 HTTP 方式运行，带信号处理和优雅退出"""
    import uvicorn

    if cfg.transport == "sse":
        app = mcp.sse_app()
    else:
        app = mcp.streamable_http_app()

    if cfg.api_key:
        app.add_middleware(_AuthMiddleware, api_key=cfg.api_key)
        logger.info("API Key 鉴权已启用")
    else:
        logger.warning("未设置 SEARCHMCP_API_KEY，服务无鉴权保护")

    config = uvicorn.Config(
        app,
        host=cfg.host,
        port=cfg.port,
        log_level=mcp.settings.log_level.lower(),
        timeout_graceful_shutdown=5,
    )
    server = uvicorn.Server(config)

    logger.info(
        "使用 %s 传输启动 http://%s:%d，SSE 端点: http://%s:%d/sse",
        cfg.transport, cfg.host, cfg.port, cfg.host, cfg.port,
    )

    try:
        anyio.run(server.serve)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logger.info("服务已停止")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )

    parser = argparse.ArgumentParser(description="SearchMCP - 多后端在线搜索 MCP Server")
    parser.add_argument(
        "-f", "--config",
        default=None,
        help="配置文件路径（TOML 格式），环境变量优先级高于配置文件",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    init(cfg)

    if cfg.transport == "stdio":
        logger.info("使用 stdio 传输启动")
        mcp.run(transport="stdio")
    else:
        _run_http(cfg)
