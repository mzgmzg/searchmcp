# SearchMCP

多后端在线搜索 MCP Server。为 AI 提供 web 搜索能力，支持 DuckDuckGo（免费）、Brave、Tavily、Bing。

## 技术栈

- Python 3.11+，使用 `mcp[cli]` 库（FastMCP）
- `uv` 管理虚拟环境和依赖
- `ddgs` 库提供 DuckDuckGo 搜索
- `httpx` 用于商业 API 后端的 HTTP 请求
- 通过 stdio 传输与 Claude Code 通信

## 项目结构

```
searchmcp/
├── pyproject.toml          # 项目配置、依赖、入口点
├── Makefile                # 常用命令（make help 查看）
├── src/searchmcp/
│   ├── server.py           # FastMCP 应用，动态注册 tool，main()
│   ├── base.py             # SearchResult 数据类 + SearchBackend 抽象基类
│   ├── registry.py         # get_backends() 根据环境变量激活后端
│   ├── duckduckgo.py       # DuckDuckGoBackend（免费，无需 Key，默认启用）
│   ├── brave.py            # BraveBackend（需 BRAVE_API_KEY）
│   ├── tavily.py           # TavilyBackend（需 TAVILY_API_KEY）
│   └── bing.py             # BingBackend（需 BING_API_KEY）
```

## 架构

### 抽象基类 (base.py)

`SearchBackend` 是抽象基类，定义了两个类属性和一个抽象方法：
- `name` — 后端标识，用于生成 MCP tool 名称（如 `search_duckduckgo`）
- `description` — 给 LLM 看的工具描述
- `search(query, max_results)` — 异步搜索方法，返回 `SearchResult` 列表

`SearchResult` 包含 `title`, `url`, `snippet` 三个字段，`__str__` 输出 Markdown 格式。

### 后端激活 (registry.py)

- DuckDuckGo 始终激活（免费免 Key）
- Brave / Tavily / Bing 仅在对应环境变量已设置时激活
- 返回后端类列表，server.py 逐一实例化并注册为 MCP tool

### 添加新后端

1. 新建 `src/searchmcp/yourbackend.py`，继承 `SearchBackend`，实现 `search()` 方法
2. 在 `registry.py` 的 `get_backends()` 中添加对应的环境变量判断

## 常用命令

```bash
make install       # 安装依赖
make run           # 启动 server（仅 DuckDuckGo）
make test-brave    # 启动 server + Brave 后端
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
        "run", "searchmcp"
      ]
    }
  }
}
```

启用商业 API 后端时加入 `env` 字段即可。
