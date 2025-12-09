"""Application configuration."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me-in-production"
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:5173"]


def get_config() -> Config:
    """Get configuration from environment."""
    return Config(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        database_url=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
        secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
    )

