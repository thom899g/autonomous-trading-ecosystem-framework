"""
Centralized configuration management with environment validation.
Handles all sensitive credentials and trading parameters.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TradingMode(Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"

@dataclass
class ExchangeConfig:
    """Configuration for cryptocurrency exchanges"""
    name: str
    api_key: str
    api_secret: str
    testnet: bool = False
    rate_limit: int = 1000  # ms between requests
    
    def validate(self) -> bool:
        """Validate exchange credentials"""
        if not self.api_key or not self.api_secret:
            logging.error(f"Missing credentials for {self.name}")
            return False
        if len(self.api_key) < 20 or len(self.api_secret) < 20:
            logging.warning(f"Credentials for {self.name} appear too short")
        return True

@dataclass
class FirebaseConfig:
    """Firebase configuration (CRITICAL for ecosystem)"""
    project_id: str
    credentials_path: str
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        if not os.path.exists(self.credentials_path):
            logging.error(f"Firebase credentials file not found: {self.credentials_path}")
            return False
        if not self.project_id:
            logging.error("Firebase project ID is required")
            return False
        return True

class Config:
    """Main configuration class with validation"""
    
    def __init__(self):
        # Trading parameters
        self.trading_mode = TradingMode(os.getenv("TRADING_MODE", "PAPER"))
        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", 0.1))
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", 0.02))
        
        # Exchange configurations
        self.exchanges: Dict[str, ExchangeConfig] = {}
        self._load_exchanges()
        
        # Firebase configuration
        self.firebase = FirebaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        )
        
        # Telegram configuration
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Validate all configurations
        self.validate()
    
    def _load_exchanges(self):
        """Load all configured exchanges from environment"""
        # Example: Binance configuration
        if os.getenv("BINANCE_API_KEY"):
            self.exchanges["binance"] = ExchangeConfig(
                name="binance",
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                testnet=os.getenv("BINANCE_TESTNET", "false").lower() == "true"
            )
    
    def validate(self) -> None:
        """Validate all configurations and raise errors for critical issues"""
        errors = []
        
        # Validate trading parameters
        if self.max_position_size <= 0 or self.max_position_size > 1:
            errors.append("MAX_POSITION_SIZE must be between 0 and 1")
        if self.max_daily_loss <= 0 or self.max_daily_loss > 0.5:
            errors.append("MAX_DAILY_LOSS must be between 0 and 0.5")
        
        # Validate at least one exchange
        if not self.exchanges:
            errors.append("No exchange configurations found")
        else:
            for name, exchange in self.exchanges.items():
                if not exchange.validate():
                    errors.append(f"Invalid configuration for {name}")
        
        # Validate Firebase (CRITICAL)
        if not self.firebase.validate():
            errors.append("Firebase configuration invalid")
        
        if errors:
            error_msg = "\n".join(errors)
            logging.critical(f"Configuration errors:\n{error_msg}")
            raise ValueError(f"Configuration validation failed: {error_msg}")
        
        logging.info("Configuration validated successfully")
    
    def get_active_exchanges(self) -> Dict[str, ExchangeConfig]:
        """Return only validated exchange configurations"""
        return {k: v for k, v in self.exchanges.items() if v.validate()}

# Global configuration instance
config = Config()