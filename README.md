# SearchMCP

多后端在线搜索 MCP Server，支持 DuckDuckGo（免费）、Brave、Tavily、Bing，以及网页抓取。

## 快速开始

```bash
make install
make run
```

## 工具列表

| Tool 名称 | 说明 | 依赖 |
|-----------|------|------|
| `search_duckduckgo` | DuckDuckGo 搜索，免费免 Key | 默认启用 |
| `search_brave` | Brave Search API 搜索 | `BRAVE_API_KEY` |
| `search_tavily` | Tavily Search API 搜索 | `TAVILY_API_KEY` |
| `search_bing` | Bing Web Search API 搜索 | `BING_API_KEY` |
| `fetch` | 抓取指定 URL 的网页内容，返回纯文本 | 默认启用 |

## 传输方式

| 模式 | 命令 | 适用场景 |
|------|------|----------|
| stdio | `make run` | Claude Code 本地集成 |
| HTTP/SSE | `make run-http` | 远程客户端连接 |

HTTP 模式下默认监听 `http://127.0.0.1:8000/sse`，可通过环境变量自定义：

```bash
FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=9000 make run-http
```

### API Key 鉴权

HTTP 模式下可设置 `SEARCHMCP_API_KEY` 启用鉴权，客户端需在请求头中携带 `Authorization: Bearer <key>`：

```bash
SEARCHMCP_API_KEY=my-secret make run-http
```

不设置该变量时无鉴权，向后兼容。

## 集成到 Claude Code

在 `.claude/settings.local.json` 中添加：

```json
{
  "mcpServers": {
    "searchmcp": {
      "command": "uv",
      "args": ["--directory", "/Users/mazhiguo/workspace-cli/searchmcp", "run", "searchmcp"]
    }
  }
}
```

启用商业后端时，在 `env` 中传入 API Key：

```json
{
  "mcpServers": {
    "searchmcp": {
      "command": "uv",
      "args": ["--directory", "/Users/mazhiguo/workspace-cli/searchmcp", "run", "searchmcp"],
      "env": {
        "BRAVE_API_KEY": "your-key-here"
      }
    }
  }
}
```

## 添加新后端

1. 创建 `src/searchmcp/yourbackend.py`：

```python
from searchmcp.base import SearchBackend, SearchResult

class YourBackend(SearchBackend):
    name = "yourbackend"
    description = "Search the web using YourBackend."

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        # 在这里实现搜索逻辑
        return [...]
```

2. 在 `src/searchmcp/registry.py` 中注册：

```python
from searchmcp.yourbackend import YourBackend

def get_backends():
    backends = [DuckDuckGoBackend]
    if os.environ.get("YOUR_API_KEY"):
        backends.append(YourBackend)
    return backends
```
