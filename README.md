# SearchMCP

多后端在线搜索 MCP Server，为 AI 提供 web 搜索和网页抓取能力。

## 快速开始

```bash
# 安装依赖
make install

# 启动（stdio 模式，Claude Code 集成用）
make run

# 启动 HTTP 模式
make run-http
```

## 功能

### 搜索工具

| Tool | 后端 | 需要 API Key |
|------|------|--------------|
| `search_duckduckgo` | DuckDuckGo | 否，免费 |
| `search_brave` | Brave Search | `BRAVE_API_KEY` |
| `search_tavily` | Tavily Search | `TAVILY_API_KEY` |
| `search_bing` | Bing Web Search | `BING_API_KEY` |

- DuckDuckGo 默认启用，无需任何配置
- 其他后端仅在设置了对应的环境变量时自动激活
- 每个后端注册为独立的 MCP tool，AI 可以按需选择

### 网页抓取

| Tool | 说明 |
|------|------|
| `fetch` | 抓取指定 URL，自动剥离 HTML 返回纯文本，支持 1MB 上限和重定向 |

### 传输方式

| 模式 | 命令 | 适用场景 |
|------|------|----------|
| stdio | `make run` | Claude Code / Cursor 本地集成 |
| HTTP/SSE | `make run-http` | 远程客户端、多端共享 |

HTTP 模式默认 `http://127.0.0.1:8000/sse`，可自定义地址和端口：

```bash
FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=9000 make run-http
```

### API Key 鉴权

HTTP 模式下可启用鉴权，设置环境变量即可：

```bash
SEARCHMCP_API_KEY=my-secret make run-http
```

客户端请求时需携带 `Authorization: Bearer my-secret` 头。不设置该变量则无鉴权。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SEARCHMCP_TRANSPORT` | 传输方式：`stdio` / `sse` / `streamable-http` | `stdio` |
| `SEARCHMCP_API_KEY` | HTTP 模式的 API Key，不设则无鉴权 | 空 |
| `FASTMCP_HOST` | HTTP 监听地址 | `127.0.0.1` |
| `FASTMCP_PORT` | HTTP 监听端口 | `8000` |
| `BRAVE_API_KEY` | 激活 Brave Search 后端 | 空 |
| `TAVILY_API_KEY` | 激活 Tavily Search 后端 | 空 |
| `BING_API_KEY` | 激活 Bing Search 后端 | 空 |

## Claude Code 集成

`.claude/settings.local.json`：

```json
{
  "mcpServers": {
    "searchmcp": {
      "command": "uv",
      "args": [
        "--directory", "/Users/mazhiguo/workspace-cli/searchmcp",
        "run", "searchmcp"
      ]
    }
  }
}
```

启用商业搜索后端：

```json
{
  "mcpServers": {
    "searchmcp": {
      "command": "uv",
      "args": ["--directory", "/Users/mazhiguo/workspace-cli/searchmcp", "run", "searchmcp"],
      "env": {
        "BRAVE_API_KEY": "your-key"
      }
    }
  }
}
```

## 项目结构

```
searchmcp/
├── pyproject.toml
├── Makefile
├── src/searchmcp/
│   ├── server.py         # FastMCP 应用，工具注册，入口 main()
│   ├── base.py           # SearchResult 数据类 + SearchBackend 抽象基类
│   ├── registry.py       # 根据环境变量激活后端
│   ├── duckduckgo.py     # DuckDuckGoBackend
│   ├── brave.py          # BraveBackend
│   ├── tavily.py         # TavilyBackend
│   └── bing.py           # BingBackend
```

## 添加新后端

1. 创建 `src/searchmcp/yourbackend.py`，继承 `SearchBackend`：

```python
from searchmcp.base import SearchBackend, SearchResult

class YourBackend(SearchBackend):
    name = "yourbackend"
    description = "Search the web using YourBackend."

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        ...
```

2. 在 `src/searchmcp/registry.py` 中注册：

```python
if os.environ.get("YOUR_API_KEY"):
    backends.append(YourBackend)
```
