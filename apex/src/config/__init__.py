import logging
from os import getcwd
from functools import lru_cache
from typing import ClassVar, Optional
from pydantic import BaseSettings, Field, root_validator, validator
from dash_bootstrap_components import icons
from pydantic import BaseModel as PydanticBaseModel, BaseConfig

log = logging


class BaseModel(PydanticBaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True
        

class Settings(BaseSettings):
    
    extensions: ClassVar[list[str]] = ['auth','cache','database', 'migrate', 'commands', 'session','celery']

    environment: str = Field("development", env="ENVIRONMENT")
    folder_assets: str = Field(default_factory=lambda: f'{getcwd()}/assets')
    limit: int = Field(1500, env="LIMIT")
    base_url: str = Field("/", env="BASE_URL")
    root_domain: Optional[str] = Field(None, env="ROOT_DOMAIN")
    default_tenant_slug: str = Field("default", env="DEFAULT_TENANT_SLUG")
    bootstrap_admin_username: Optional[str] = Field(None, env="BOOTSTRAP_ADMIN_USERNAME")
    bootstrap_admin_password: Optional[str] = Field(None, env="BOOTSTRAP_ADMIN_PASSWORD")
    redis_db: str = Field("redis://redis:6379", env="REDIS_HOST")
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    secure_cookies: Optional[bool] = Field(None, env="SESSION_COOKIE_SECURE")
    credentials_secret_key: Optional[str] = Field(None, env="CREDENTIALS_SECRET_KEY")
    celery_result_expires_seconds: int = Field(604800, env="CELERY_RESULT_EXPIRES_SECONDS")
    celery_task_soft_time_limit_seconds: int = Field(600, env="CELERY_TASK_SOFT_TIME_LIMIT_SECONDS")
    celery_task_time_limit_seconds: int = Field(660, env="CELERY_TASK_TIME_LIMIT_SECONDS")
    external_request_timeout_seconds: int = Field(30, env="EXTERNAL_REQUEST_TIMEOUT_SECONDS")
    openai_timeout_seconds: int = Field(60, env="OPENAI_TIMEOUT_SECONDS")
    smtp_timeout_seconds: int = Field(30, env="SMTP_TIMEOUT_SECONDS")
    search_results_per_source: int = Field(10, env="SEARCH_RESULTS_PER_SOURCE")

    secret_session: str = Field("dev-secret-session-change-me", env="SECRET_SESSION")
    theme_default: str = 'BOOTSTRAP'
    theme_icon = icons.BOOTSTRAP

    @validator("environment")
    def validate_environment(cls, value):
        allowed = {"development", "staging", "production"}
        normalized = value.lower().strip()
        if normalized not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @root_validator
    def validate_required_production_settings(cls, values):
        environment = values.get("environment")
        is_production_like = environment in {"staging", "production"}
        secret_session = values.get("secret_session")
        database_url = values.get("database_url")
        redis_db = values.get("redis_db")
        secure_cookies = values.get("secure_cookies")

        if not is_production_like:
            return values

        missing = []
        if not secret_session or secret_session in {
            "dev-secret-session-change-me",
            "change-me-in-production",
            "replace-with-a-long-random-secret",
        }:
            missing.append("SECRET_SESSION")
        if not redis_db:
            missing.append("REDIS_HOST")
        if not database_url:
            missing.append("DATABASE_URL")
        if secure_cookies is False:
            missing.append("SESSION_COOKIE_SECURE=true")
        if not values.get("credentials_secret_key") or values.get("credentials_secret_key") in {
            "dev-credentials-secret-change-me",
            "replace-with-a-long-random-credentials-secret",
        }:
            missing.append("CREDENTIALS_SECRET_KEY")

        if missing:
            raise ValueError(
                f"Missing or unsafe production settings for {environment}: {', '.join(missing)}"
            )

        return values

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_production_like(self) -> bool:
        return self.environment in {"staging", "production"}

    @property
    def use_secure_cookies(self) -> bool:
        if self.secure_cookies is not None:
            return self.secure_cookies
        return self.is_production_like
        
    class Config:
        env_nested_delimiter = '__'
        
    
@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
