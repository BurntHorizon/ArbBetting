"""Configuration management with validation for the arbitrage backend service."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Config:
    """Application configuration with validation."""

    # API Configuration
    ODDS_API_KEY: str
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com/v4"

    # Database Configuration
    DATABASE_URL: str

    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str
    ALERT_TO_NUMBER: Optional[str]

    # Application Settings
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Bookmaker Settings
    NY_BOOKIES: str = "draftkings,fanduel,betmgm,caesars,pointsbet,wynnbet,bet365,barstool"

    def __init__(self):
        """Initialize and validate configuration."""
        self._load_config()
        self._validate_config()

    def _load_config(self):
        """Load configuration from environment variables."""
        self.ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
        self.ODDS_API_BASE_URL = os.getenv("ODDS_API_BASE_URL", self.ODDS_API_BASE_URL)

        self.DATABASE_URL = os.getenv("DATABASE_URL", "")

        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
        self.ALERT_TO_NUMBER = os.getenv("ALERT_TO_NUMBER")

        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", self.ENVIRONMENT)

        self.NY_BOOKIES = os.getenv("NY_BOOKIES", self.NY_BOOKIES)

    def _validate_config(self):
        """Validate required configuration values."""
        errors = []

        if not self.ODDS_API_KEY:
            errors.append("ODDS_API_KEY is required")

        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")

        if not self.TWILIO_ACCOUNT_SID:
            errors.append("TWILIO_ACCOUNT_SID is required")

        if not self.TWILIO_AUTH_TOKEN:
            errors.append("TWILIO_AUTH_TOKEN is required")

        if not self.TWILIO_FROM_NUMBER:
            errors.append("TWILIO_FROM_NUMBER is required")

        if errors:
            raise ConfigError(
                "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"


# Global configuration instance
config = Config()
