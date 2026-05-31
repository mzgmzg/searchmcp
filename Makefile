.PHONY: help install run run-http clean test-brave test-bing test-tavily

.DEFAULT_GOAL := help

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	uv sync

run: ## 启动服务 stdio 模式（Claude Code 集成用）
	uv run python -m searchmcp

run-http: ## 启动服务 HTTP 模式（默认监听 127.0.0.1:8000）
	SEARCHMCP_TRANSPORT=sse uv run python -m searchmcp

clean: ## 清理虚拟环境和缓存文件
	rm -rf .venv __pycache__ src/searchmcp/__pycache__

test-brave: ## 启动服务并启用 Brave 后端（需设置 BRAVE_API_KEY 环境变量）
	BRAVE_API_KEY=$(BRAVE_API_KEY) uv run python -m searchmcp

test-bing: ## 启动服务并启用 Bing 后端（需设置 BING_API_KEY 环境变量）
	BING_API_KEY=$(BING_API_KEY) uv run python -m searchmcp

test-tavily: ## 启动服务并启用 Tavily 后端（需设置 TAVILY_API_KEY 环境变量）
	TAVILY_API_KEY=$(TAVILY_API_KEY) uv run python -m searchmcp
