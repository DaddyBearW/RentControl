from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./rentcontrol.db"
    secret_key: str = "change-this-secret-in-production"
    access_token_expire_minutes: int = 1440
    admin_email: str = "admin@rentcontrol.local"
    admin_password: str = "Admin12345!"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
