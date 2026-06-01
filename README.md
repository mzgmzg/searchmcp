# SearchMCP

多后端在线搜索 MCP Server，为 AI 提供 web 搜索和网页抓取能力。

## 快速开始

```bash
make install   # 安装依赖
make run       # 启动（stdio 模式）
```

## 功能

### 搜索工具

| Tool | 后端 | 激活方式 |
|------|------|----------|
| `search_duckduckgo` | DuckDuckGo | 默认启用，免费 |
| `search_brave` | Brave Search | 配置 `brave_api_key` |
| `search_tavily` | Tavily Search | 配置 `tavily_api_key` |
| `search_bing` | Bing Web Search | 配置 `bing_api_key` |

### 网页抓取

| Tool | 说明 |
|------|------|
| `fetch` | 抓取指定 URL，自动剥离 HTML 返回纯文本 |

## 配置

配置优先级：**环境变量 > 配置文件 > 默认值**。

### 配置文件

复制 `searchmcp.example.toml` 为 `searchmcp.toml` 并按需修改：

```toml
[server]
transport = "stdio"          # stdio / sse / streamable-http
host = "127.0.0.1"
port = 8000
api_key = ""                 # HTTP 鉴权用，不设置则无鉴权

[search]
proxy = ""                   # HTTP 代理，如 http://127.0.0.1:7890
brave_api_key = ""
tavily_api_key = ""
bing_api_key = ""
```

指定配置文件：

```bash
# -f 参数
uv run python -m searchmcp -f searchmcp.toml

# 或通过环境变量
SEARCHMCP_CONFIG=/path/to/config.toml uv run python -m searchmcp
```

### 环境变量

所有配置项都有对应的环境变量，可覆盖配置文件中的值：

| 环境变量 | 配置文件键 | 默认值 |
|---------|-----------|--------|
| `SEARCHMCP_TRANSPORT` | `server.transport` | `stdio` |
| `FASTMCP_HOST` | `server.host` | `127.0.0.1` |
| `FASTMCP_PORT` | `server.port` | `8000` |
| `SEARCHMCP_API_KEY` | `server.api_key` | 空 |
| `SEARCHMCP_PROXY` | `search.proxy` | 空 |
| `SEARCHMCP_CONFIG` | — | 空 |
| `BRAVE_API_KEY` | `search.brave_api_key` | 空 |
| `TAVILY_API_KEY` | `search.tavily_api_key` | 空 |
| `BING_API_KEY` | `search.bing_api_key` | 空 |

### 命令行参数

```
python -m searchmcp -f searchmcp.toml
```

| 参数 | 说明 |
|------|------|
| `-f`, `--config` | 配置文件路径 |

## 传输方式

| 模式 | 命令 | 适用场景 |
|------|------|----------|
| stdio | `make run` | Claude Code / Cursor 本地集成 |
| HTTP/SSE | `make run-http` | 远程客户端、多端共享 |

HTTP 模式默认监听 `http://127.0.0.1:8000/sse`。启用鉴权：

```bash
SEARCHMCP_API_KEY=my-secret make run-http
```

客户端需携带 `Authorization: Bearer my-secret` 头，不设置则无鉴权。

## 代理

设置 HTTP 代理后，所有搜索请求和 fetch 请求均通过代理发出：

```bash
# 环境变量
SEARCHMCP_PROXY=http://192.168.100.210:7893 make run

# 或在配置文件中设置 search.proxy
```

## Claude Code 集成

`.claude/settings.local.json`：

```json
{
  "mcpServers": {
    "searchmcp": {
      "command": "uv",
      "args": [
        "--directory", "/Users/mazhiguo/workspace-cli/searchmcp",
        "run", "searchmcp",
        "-f", "/Users/mazhiguo/workspace-cli/searchmcp/searchmcp.toml"
      ]
    }
  }
}
```

或纯环境变量方式：

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
├── searchmcp.example.toml    # 配置文件示例
├── Makefile
├── src/searchmcp/
│   ├── server.py             # FastMCP 应用，工具注册，入口 main()
│   ├── config.py             # 统一配置加载（TOML + 环境变量）
│   ├── base.py               # SearchResult 数据类 + SearchBackend 抽象基类
│   ├── registry.py           # 根据配置激活后端
│   ├── duckduckgo.py         # DuckDuckGoBackend
│   ├── brave.py              # BraveBackend
│   ├── tavily.py             # TavilyBackend
│   └── bing.py               # BingBackend
```

## 添加新后端

1. 创建 `src/searchmcp/yourbackend.py`，继承 `SearchBackend`：

```python
from searchmcp.base import SearchBackend, SearchResult

class YourBackend(SearchBackend):
    name = "yourbackend"
    description = "Search the web using YourBackend."

    def __init__(self, api_key: str = "", proxy: str = ""):
        self.api_key = api_key
        self.proxy = proxy

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        ...
```

2. 在 `src/searchmcp/registry.py` 中注册：

```python
if cfg.your_api_key:
    backends.append(YourBackend(api_key=cfg.your_api_key, proxy=cfg.proxy))
```

3. 在 `src/searchmcp/config.py` 的 `Config` 和 `_apply_env` 中添加对应的配置项。
