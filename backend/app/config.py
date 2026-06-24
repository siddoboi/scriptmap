from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    allowed_origins: list[str] = ["http://localhost:5173"]
    environment: str = "development"
    log_level: str = "INFO"

    # File handling
    max_file_size_mb: int = 5
    tmp_dir: str = "/tmp/scriptmap"
    parse_timeout_sec: int = 15

    # Session
    session_ttl_minutes: int = 60

    # Optional integrations
    sentry_dsn: str | None = None

    model_config = {"env_file": ".env"}


settings = Settings()