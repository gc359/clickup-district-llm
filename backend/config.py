from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    clickup_token: str = ""
    clickup_team_id: str = ""
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss-safeguard:20b"
    max_steps: int = 5
    cors_origins: str = "http://localhost:5173"
    clickup_ticket_list_name: str = "Support Tickets"
    clickup_kb_folder_name: str = "Knowledge Base"

    @field_validator("ollama_host")
    @classmethod
    def _ensure_scheme(cls, v: str) -> str:
        if v and not v.startswith(("http://", "https://")):
            return f"http://{v}"
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
