from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"  # overridden in Docker via DATABASE_URL env var
    app_env: str = "development"
    workers: int = 1

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
