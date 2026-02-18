import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DEFAULTS = {
    "DB_URL": "sqlite:///vanta.db",
    "SMTP_HOST": "localhost",
    "SMTP_PORT": "1025",
    "SMTP_USER": "",
    "SMTP_PASS": "",
    "SMTP_TLS": "false",
    "EDGE_ENABLED": "false",
    "EDGE_HOST": "0.0.0.0",
    "EDGE_PORT": "8080",
    "RATE_LIMIT_PER_MINUTE": "120",
    "ALLOW_IPS": "",
    "DENY_IPS": "",
    "UPSTREAM_HTTP": ""
}

SENSITIVE_KEYS = {"SMTP_PASS", "DB_URL"}

def get(key: str) -> str:
    return os.environ.get(key, DEFAULTS.get(key, ""))

def all_config() -> Dict[str, Any]:
    cfg = {k: os.environ.get(k, v) for k, v in DEFAULTS.items()}
    return cfg

def sanitized() -> Dict[str, Any]:
    cfg = all_config()
    for k in list(cfg.keys()):
        if k in SENSITIVE_KEYS and cfg.get(k):
            cfg[k] = "***"
    return cfg

def get_int(key: str, default: int) -> int:
    try:
        return int(get(key))
    except Exception:
        return default

def get_list(key: str) -> list[str]:
    raw = get(key)
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]
