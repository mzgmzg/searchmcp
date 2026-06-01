import os
import tomllib
from dataclasses import dataclass


@dataclass
class Config:
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    api_key: str = ""
    proxy: str = ""
    brave_api_key: str = ""
    tavily_api_key: str = ""
    bing_api_key: str = ""


def load_config(path: str | None = None) -> Config:
    cfg = Config()

    config_path = path or os.environ.get("SEARCHMCP_CONFIG")
    if config_path:
        _load_file(cfg, config_path)

    _apply_env(cfg)
    return cfg


def _load_file(cfg: Config, path: str):
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return

    server = data.get("server", {})
    search = data.get("search", {})

    for key in ("transport", "host", "api_key"):
        if key in server:
            setattr(cfg, key, server[key])
    if "port" in server:
        cfg.port = server["port"]

    for key in ("proxy", "brave_api_key", "tavily_api_key", "bing_api_key"):
        if key in search:
            setattr(cfg, key, search[key])


def _apply_env(cfg: Config):
    env_map = {
        "SEARCHMCP_TRANSPORT": "transport",
        "FASTMCP_HOST": "host",
        "FASTMCP_PORT": "port",
        "SEARCHMCP_API_KEY": "api_key",
        "SEARCHMCP_PROXY": "proxy",
        "BRAVE_API_KEY": "brave_api_key",
        "TAVILY_API_KEY": "tavily_api_key",
        "BING_API_KEY": "bing_api_key",
    }
    for env_key, attr in env_map.items():
        val = os.environ.get(env_key)
        if val:
            setattr(cfg, attr, int(val) if attr == "port" else val)
