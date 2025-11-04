"""
Configuration management for the crypto arbitrage bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for the arbitrage bot."""
    
    # Exchange API Keys
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET = os.getenv('BINANCE_SECRET', '')
    KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY', '')
    KRAKEN_SECRET = os.getenv('KRAKEN_SECRET', '')
    
    # Trading Configuration
    MIN_PROFIT_PERCENTAGE = float(os.getenv('MIN_PROFIT_PERCENTAGE', '0.5'))
    TRADE_AMOUNT_USD = float(os.getenv('TRADE_AMOUNT_USD', '100'))
    DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    # Monitoring Configuration
    CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '10'))
    TRADING_PAIRS = os.getenv('TRADING_PAIRS', 'BTC/USDT,ETH/USDT').split(',')
    EXCHANGES = os.getenv('EXCHANGES', 'binance,kraken').split(',')
    
    # Risk Management
    MAX_SLIPPAGE_PERCENTAGE = 0.3
    ORDER_TIMEOUT_SECONDS = 30
    TRADING_FEE_PERCENTAGE = 0.2  # Estimated total fee (0.1% per trade)
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if cls.MIN_PROFIT_PERCENTAGE < 0:
            raise ValueError("MIN_PROFIT_PERCENTAGE must be non-negative")
        if cls.TRADE_AMOUNT_USD <= 0:
            raise ValueError("TRADE_AMOUNT_USD must be positive")
        if cls.CHECK_INTERVAL_SECONDS <= 0:
            raise ValueError("CHECK_INTERVAL_SECONDS must be positive")
        if not cls.TRADING_PAIRS:
            raise ValueError("At least one trading pair must be specified")
        if not cls.EXCHANGES:
            raise ValueError("At least one exchange must be specified")
        return True
