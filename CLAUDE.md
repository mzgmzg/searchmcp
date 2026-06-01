# SearchMCP

多后端在线搜索 MCP Server。为 AI 提供 web 搜索和网页抓取能力，支持 DuckDuckGo（免费）、Brave、Tavily、Bing。

## 技术栈

- Python 3.11+，使用 `mcp[cli]` 库（FastMCP）
- `uv` 管理虚拟环境和依赖
- `ddgs` 库提供 DuckDuckGo 搜索
- `httpx` 用于商业 API 后端 HTTP 请求和 fetch 工具
- 支持 stdio 和 HTTP/SSE 两种传输方式

## 项目结构

```
searchmcp/
├── pyproject.toml              # 项目配置、依赖、入口点
├── searchmcp.example.toml      # 配置文件示例
├── Makefile                    # 常用命令（make help 查看）
├── src/searchmcp/
│   ├── server.py               # FastMCP 应用，动态注册 tool，入口 main()
│   ├── config.py               # 统一配置加载（TOML + 环境变量）
│   ├── base.py                 # SearchResult 数据类 + SearchBackend 抽象基类
│   ├── registry.py             # 根据 Config 激活后端并实例化
│   ├── duckduckgo.py           # DuckDuckGoBackend（免费，默认启用）
│   ├── brave.py                # BraveBackend（需 api_key）
│   ├── tavily.py               # TavilyBackend（需 api_key）
│   └── bing.py                 # BingBackend（需 api_key）
```

## 架构

### 配置系统 (config.py)

- `Config` 数据类包含所有配置项，带默认值
- `load_config(path)` 加载顺序：默认值 → 配置文件(TOML) → 环境变量（覆盖）
- `-f` / `--config` 命令行参数指定配置文件
- `SEARCHMCP_CONFIG` 环境变量也可以指定配置文件路径
- **用户本地配置文件 `searchmcp.toml` 在 .gitignore 中，不可提交**

### 抽象基类 (base.py)

`SearchBackend` 抽象基类：
- `name` — 后端标识，用于生成 MCP tool 名称
- `description` — 给 LLM 看的工具描述
- `search(query, max_results)` — 异步搜索方法，返回 `SearchResult` 列表

`SearchResult` 包含 `title`, `url`, `snippet`，`__str__` 输出 Markdown 格式。

### 后端激活 (registry.py)

- 接收 `Config` 对象
- DuckDuckGo 始终激活，传入 proxy
- Brave / Tavily / Bing 仅在 config 中对应的 api_key 非空时激活，传入 api_key 和 proxy
- 返回已实例化的后端列表，server.py 逐一注册为 MCP tool

### 后端构造函数

所有后端统一接收构造参数，不再自己读环境变量：
- `__init__(self, api_key="", proxy="")` — api_key 用于商业 API，DuckDuckGo 不需要
- `proxy` 传给 `httpx.AsyncClient(proxy=...)` 或 `DDGS(proxy=...)`

### 工具注册 (server.py)

- 搜索后端：遍历 `get_backends(cfg)` 返回的实例，注册 `search_{name}` tool
- `fetch` tool：通用网页抓取，通过 httpx + proxy 实现
- `_AuthMiddleware`：HTTP 模式下可选的 API Key 鉴权，检查 `Authorization: Bearer <key>` 头
- `_run_http()`：创建 uvicorn server，`timeout_graceful_shutdown=5` 实现优雅退出

### 添加新后端

1. 创建 `src/searchmcp/yourbackend.py`，继承 `SearchBackend`，构造函数接收 `api_key` 和 `proxy`
2. 在 `registry.py` 的 `get_backends()` 中添加激活判断和实例化
3. 在 `config.py` 的 `Config` 和 `_apply_env()` 中添加对应配置项和环境变量映射

## 常用命令

```bash
make install       # 安装依赖
make run           # 启动 server（stdio 模式，DuckDuckGo）
make run-http      # 启动 HTTP/SSE 模式
make test-brave    # 启动 server + Brave 后端
make clean         # 清理虚拟环境和缓存
make help          # 查看所有命令
```

## Claude Code 集成

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

## 配置文件格式

参考 `searchmcp.example.toml`，复制为 `searchmcp.toml` 后修改。所有配置项也可通过环境变量覆盖，环境变量优先级更高。

```toml
[server]
transport = "stdio"
host = "127.0.0.1"
port = 8000
api_key = ""

[search]
proxy = ""
brave_api_key = ""
tavily_api_key = ""
bing_api_key = ""
```
