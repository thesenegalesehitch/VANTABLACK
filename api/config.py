import os
import yaml
from typing import Optional, List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings

class TelegramSettings(BaseSettings):
    enabled: bool = False
    token: Optional[str] = None
    chat_id: Optional[str] = None

class DiscordSettings(BaseSettings):
    enabled: bool = False
    webhook_url: Optional[str] = None

class EvasionSettings(BaseSettings):
    stealth_level: int = 3
    sandbox_detect: bool = True
    gpu_fingerprint: bool = True
    battery_check: bool = True
    automation_check: bool = True
    vm_detect: bool = True
    user_agent_rotation: bool = True
    canvas_randomization: bool = True
    webrtc_blocking: bool = False

class ProxySettings(BaseSettings):
    enabled: bool = False
    rotation: str = "round-robin"
    list_file: str = "proxies.txt"

class DatabaseSettings(BaseSettings):
    path: str = "hitch_vault.db"
    encryption: bool = True
    auto_backup: bool = True
    backup_interval: int = 3600

class CORSSettings(BaseSettings):
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

class LoggingSettings(BaseSettings):
    level: str = "INFO"
    file: str = "vanta.log"
    max_size: int = 10485760
    backup_count: int = 5
    log_captures: bool = True
    log_connections: bool = True
    log_errors: bool = True

class EngineSettings(BaseSettings):
    evilginx_path: str = "./bin/evilginx"
    evilginx_phishlets_path: str = "./phishlets"
    evilginx_api_port: int = 5433
    evilginx_web_port: int = 443
    gophish_path: str = "./bin/gophish"
    gophish_config: str = "./configs/config.json"
    gophish_admin_port: int = 3333
    gophish_phish_port: int = 80

class Settings(BaseSettings):
    name: str = "VANTABLACK"
    version: str = "4.0.0"
    description: str = "Industrial Phishing Orchestrator - Red Team Edition"
    secret_key: str = "change_me_in_production"
    
    cors: CORSSettings = CORSSettings()
    telegram: TelegramSettings = TelegramSettings()
    discord: DiscordSettings = DiscordSettings()
    evasion: EvasionSettings = EvasionSettings()
    proxy: ProxySettings = ProxySettings()
    database: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    engines: EngineSettings = EngineSettings()

    @classmethod
    def load_from_yaml(cls, path: str = "hitch_config.yaml") -> "Settings":
        if not os.path.exists(path):
            # Fallback to example if exists, or just defaults
            example_path = path + ".example"
            if os.path.exists(example_path):
                print(f"[WARN] Config file {path} not found. Using {example_path} as template.")
                path = example_path
            else:
                return cls()
        
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
            
            # Helper to map nested dicts to pydantic models
            # This is a bit manual because BaseSettings doesn't auto-map nested dicts from yaml easily without extra libs
            # But we can construct it.
            
            # Extract nested sections
            cors_data = data.get("cors", {})
            telegram_data = data.get("telegram", {})
            discord_data = data.get("discord", {})
            evasion_data = data.get("evasion", {})
            proxy_data = data.get("proxy", {})
            database_data = data.get("database", {})
            logging_data = data.get("logging", {})
            engines_data = data.get("engines", {})
            
            # Flatten engines data for our flat EngineSettings
            evilginx_data = engines_data.get("evilginx", {})
            gophish_data = engines_data.get("gophish", {})
            
            engine_settings = EngineSettings(
                evilginx_path=evilginx_data.get("path", "./bin/evilginx"),
                evilginx_phishlets_path=evilginx_data.get("phishlets_path", "./phishlets"),
                evilginx_api_port=evilginx_data.get("api_port", 5433),
                evilginx_web_port=evilginx_data.get("web_port", 443),
                gophish_path=gophish_data.get("path", "./bin/gophish"),
                gophish_config=gophish_data.get("config", "./configs/config.json"),
                gophish_admin_port=gophish_data.get("admin_port", 3333),
                gophish_phish_port=gophish_data.get("phish_port", 80),
            )

            return cls(
                name=data.get("name", "VANTABLACK"),
                version=data.get("version", "4.0.0"),
                description=data.get("description", "Industrial Phishing Orchestrator"),
                cors=CORSSettings(**cors_data),
                telegram=TelegramSettings(**telegram_data),
                discord=DiscordSettings(**discord_data),
                evasion=EvasionSettings(**evasion_data),
                proxy=ProxySettings(**proxy_data),
                database=DatabaseSettings(**database_data),
                logging=LoggingSettings(**logging_data),
                engines=engine_settings
            )
            
        except Exception as e:
            print(f"[ERROR] Failed to load config from {path}: {e}")
            return cls()

# Global settings instance
settings = Settings.load_from_yaml()
