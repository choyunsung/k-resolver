"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql://kresolver:kresolver_password@localhost:5432/kresolver"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"
    cors_origins: str = "*"

    # Optional: MaxMind for IP to ISP
    maxmind_license_key: str = ""

    # Environment
    env: str = "development"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
