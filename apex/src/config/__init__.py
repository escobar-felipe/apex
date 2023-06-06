import os
import logging
from os import getenv, getcwd
from functools import lru_cache
from pydantic import BaseSettings
from dash_bootstrap_components import icons
from pydantic import BaseModel as PydanticBaseModel, BaseConfig

log = logging


class BaseModel(PydanticBaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True
        

class Settings(BaseSettings):
    
    extensions = ['auth','admin','cache','commands', 'database', 'session','celery']

    environment: str = getenv("ENVIRONMENT", "development")
    folder_assets: str = f'{getcwd()}/assets'
    limit: int = int(getenv('LIMIT', 1500))
    base_url = os.getenv('BASE_URL', '/')
    redis_db = os.getenv('REDIS_HOST', 'redis://localhost:6379')

    secret_session = 'd5c80696-9675-4047-98a6-acac6dfb247e'
    theme_default = 'BOOTSTRAP'
    theme_icon = icons.BOOTSTRAP
        
    class Config:
        env_nested_delimiter = '__'
        
    
@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()