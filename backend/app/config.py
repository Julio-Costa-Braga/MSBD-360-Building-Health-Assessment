from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MSBD-360"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True

    database_url: str = "sqlite:///./msbd360.db"

    class Config:
        env_file = ".env"


settings = Settings()
