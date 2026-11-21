"""Application settings, read from environment variables and the local .env file."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    # Real environment variables win over values in .env, which is only a local convenience.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service: str = "FREEPDB1"
    oracle_app_user: str = "risk_app"
    oracle_app_password: SecretStr

    # Log every SQL statement and its bind values. For local debugging only.
    sql_echo: bool = False

    @property
    def database_url(self) -> URL:
        """SQLAlchemy URL for python-oracledb. URL.create escapes special characters."""
        return URL.create(
            "oracle+oracledb",
            username=self.oracle_app_user,
            password=self.oracle_app_password.get_secret_value(),
            host=self.oracle_host,
            port=self.oracle_port,
            query={"service_name": self.oracle_service},
        )


@lru_cache
def get_settings() -> Settings:
    """Read settings once per process."""
    return Settings()
