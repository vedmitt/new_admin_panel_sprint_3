import logging
from typing import List, Optional

import backoff
from pydantic import BaseSettings, Field
from movies_models import GenresModel, MoviesModel, PersonsModel

logger = logging.getLogger(__name__)

class PostgresDsn(BaseSettings):
    dbname: str = Field(..., env="PG_DB")
    user: str = Field(..., env="PG_USER")
    password: str = Field(..., env="PG_PASSWORD")
    host: str = Field(..., env="PG_HOST")
    port: int = Field(..., env="PG_PORT")
    options: str = Field(..., env="PG_OPTIONS")


class ElasticConfig(BaseSettings):
    host: str = Field(..., env="ES_HOST")
    port: int = Field(..., env="ES_PORT")


class RedisConfig(BaseSettings):
    host: str = Field(..., env="REDIS_HOST")
    port: int = Field(..., env="REDIS_PORT")


class AppConfig(BaseSettings):
    batch_size: int = Field(..., env="BATCH_SIZE")
    frequency: int = Field(..., env="FREQUENCY")
    backoff_max_retries: int = Field(..., env="BACKOFF_MAX_RETRIES")
    elastic_indexes: List[str] = Field(..., env="ES_INDEXES")
    logging_level: int = Field(..., env="LOG_LEVEL")


APP_CONFIG = AppConfig()
POSTGRES_CONFIG = PostgresDsn()
ELASTIC_CONFIG = ElasticConfig()
REDIS_CONFIG = RedisConfig()

BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": Exception,
    "logger": logger,
    "max_tries": APP_CONFIG.backoff_max_retries,
}  

LOGGER_SETTINGS = {
    "format": "%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",  # noqa 501
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "level": APP_CONFIG.logging_level,
    "handlers": [logging.StreamHandler()],
}

PG_MODELS = {
    "movies": MoviesModel,
    "genres": GenresModel,
    "persons": PersonsModel
}
