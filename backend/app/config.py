from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MSBD-360"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    database_url: str = "sqlite:///./msbd360.db"

    @property
    def resolved_database_url(self) -> str:
        url = self.database_url or "sqlite:///./msbd360.db"
        if url.startswith("postgresql://") and "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}sslmode=require"
        return url


settings = Settings()
