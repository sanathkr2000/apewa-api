
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_", extra="ignore")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_", extra="ignore")


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "postgresql://postgres:sowji27%40@127.0.0.1:5432/postgres_test"
    DB_FORCE_ROLL_BACK: bool = True
    model_config = SettingsConfigDict(env_prefix="TEST_", extra="ignore")


@lru_cache()
def get_config(env_state: str):
    """Return the correct config based on the environment state."""
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs.get(env_state, DevConfig)()  # Default to DevConfig if not found

# Load the environment configuration from the .env file
base_config = BaseConfig()
config = get_config(base_config.ENV_STATE)

print(f"Current ENV_STATE: {base_config.ENV_STATE}")  # Debugging output for the ENV_STATE
