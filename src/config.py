"""
Configuration management for the crypto trading bot.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the bot."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._load_env_variables()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_env_variables(self):
        """Load sensitive data from environment variables."""
        self.api_key = os.getenv('API_KEY', '')
        self.api_secret = os.getenv('API_SECRET', '')
        self.exchange_name = os.getenv('EXCHANGE_NAME', self.config['exchange']['name'])
        self.trading_mode = os.getenv('TRADING_MODE', self.config['trading']['mode'])
    
    def get(self, key: str, default=None):
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    @property
    def is_paper_trading(self) -> bool:
        """Check if bot is in paper trading mode."""
        return self.trading_mode.lower() == 'paper'
    
    @property
    def is_live_trading(self) -> bool:
        """Check if bot is in live trading mode."""
        return self.trading_mode.lower() == 'live'


# Global config instance
config = None


def get_config(config_path: str = "config.yaml") -> Config:
    """Get or create global config instance."""
    global config
    if config is None:
        config = Config(config_path)
    return config
