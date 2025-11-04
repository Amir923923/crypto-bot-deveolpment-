"""
Base strategy class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger()


class Signal:
    """Trading signal class."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str, config: Dict):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            config: Strategy configuration
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Analyze market data and generate trading signal.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        pass
    
    @abstractmethod
    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the strategy.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        pass
    
    def should_execute(self) -> bool:
        """Check if strategy should execute."""
        return self.enabled
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} (enabled={self.enabled})"
