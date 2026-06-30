from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str = "Employee API Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- ODOO CONFIG ---
    ODOO_URL: str
    ODOO_API_KEY: str
    ODOO_DB: str

    # --- JWT SECURITY CONFIG (Thêm mới) ---
    SECRET_KEY: str  # Bắt buộc phải khai báo trong file .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # Mặc định token sống 24 giờ (60 * 24)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()