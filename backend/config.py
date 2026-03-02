from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://timeline:timeline_dev@localhost:5432/timeline"
    redis_url: str = "redis://localhost:6379/0"

    # AI providers (plug-and-play — change here to swap models)
    embedding_provider: str = "sentence_transformer"
    embedding_model: str = "all-MiniLM-L6-v2"
    reasoning_provider: str = "ollama"
    reasoning_model: str = "llama3.2:1b"
    ollama_base_url: str = "http://localhost:11434"

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
