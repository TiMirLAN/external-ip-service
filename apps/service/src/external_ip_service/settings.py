from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ipinfo_token: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
