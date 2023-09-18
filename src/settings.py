"""Defines project settings"""
from enum import Enum

from pydantic import IPvAnyAddress, PositiveInt
from pydantic_settings import BaseSettings


class LoggingEnum(str, Enum):
    """Logging configuration Enum."""

    critical = "CRITICAL"
    error = "ERROR"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"


class Settings(BaseSettings):
    """Project settings definition"""

    ROOT_PATH: str = ""
    LOGLEVEL: LoggingEnum = "DEBUG"
    HOST: IPvAnyAddress = "0.0.0.0"
    PORT: PositiveInt = 8000
    DEBUG_MODE: bool = True
    DB_FILEANAME: str = "db.sqlite"

    # Timezone
    DEFAULT_TIMEZONE: str = "Etc/UTC"


settings = Settings()
