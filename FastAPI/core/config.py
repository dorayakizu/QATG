from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Employee API Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    ODOO_URL: str
    ODOO_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()