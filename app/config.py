"""Encapsulates configuration"""

from dataclasses import dataclass, field


@dataclass
class Database:
    """Encapsulates configuration settings for the database."""
    driver: str = "sqlite"
    path: str = "./"
    name: str = "pmt.db"


@dataclass
class DashServer:
    """Encapsulates configuration settings for the Dash Server."""
    port: int = 8050


@dataclass
class Logger:
    """Encapsulates configuration settings for logger levels."""
    level: str = "INFO"


@dataclass
class Config:
    """Encapsulate all configurations."""
    server: DashServer
    db: Database = field(default_factory=Database)
    logger: Logger = field(default_factory=Logger)
