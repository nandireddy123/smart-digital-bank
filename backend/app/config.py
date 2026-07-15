"""
config.py
---------
Centralised application configuration.

Interview note: this is a simple example of the *Single Responsibility
Principle* (SOLID) -- this module's only job is to know how to load
configuration values. Nothing else in the app reads environment
variables directly; everything imports `settings` from here.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Database ----
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_NAME: str = os.getenv("DB_NAME", "smart_banking")

    @property
    def DATABASE_URL(self) -> str:
        from urllib.parse import quote_plus
        safe_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{safe_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ---- JWT / Auth ----
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12  # 12 hours

    # ---- OTP ----
    OTP_EXPIRE_MINUTES: int = 10

    # ---- Email (SMTP) ----
    # If SMTP_USERNAME / SMTP_PASSWORD are left blank, the app falls back
    # to printing the OTP to the console/log so you can develop locally
    # without configuring a real mail server.
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "no-reply@smartbank.local")

    # ---- App ----
    APP_NAME: str = "Smart Digital Banking Platform"
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
