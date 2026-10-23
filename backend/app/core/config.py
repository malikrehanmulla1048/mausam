"""
MAUSAM — Core Configuration
Loaded from environment variables with sensible development defaults.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "dev-secret-key-change-in-production"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    APP_VERSION: str = "1.0.0"

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "mausam_dev"

    # AWS
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # S3
    S3_BUCKET_NAME: str = "mausam-documents-dev"
    S3_REGION: str = "ap-south-1"

    # Bedrock
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_ENABLED: bool = False

    # Textract
    TEXTRACT_ENABLED: bool = False

    # Translate
    TRANSLATE_ENABLED: bool = False

    # Polly
    POLLY_ENABLED: bool = False

    # Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_APP_CLIENT_ID: str = ""
    COGNITO_ENABLED: bool = False

    # KMS
    KMS_KEY_ID: str = ""
    KMS_SIGNING_ENABLED: bool = False

    # SNS
    SNS_TOPIC_ARN: str = ""
    SNS_ENABLED: bool = False

    # SES
    SES_FROM_EMAIL: str = "noreply@mausam.example.com"
    SES_ENABLED: bool = False

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Demo
    DEMO_MODE: bool = True
    DEMO_BUSINESS_ID: str = "demo_ramesh_textiles"

    # Dev signing (fallback when KMS disabled)
    DEV_SIGNING_KEY: str = "dev-only-not-for-production"

    # Rate limit
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
