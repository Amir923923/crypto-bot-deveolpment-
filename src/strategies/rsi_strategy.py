"""
RSI (Relative Strength Index) Strategy.
"""

import pandas as pd
from typing import Dict
from src.strategies.base_strategy import BaseStrategy, Signal
from src.utils.logger import get_logger

logger = get_logger()


class RSIStrategy(BaseStrategy):
    """
    RSI Strategy.
    
    Generates BUY signal when RSI is oversold.
    Generates SELL signal when RSI is overbought.
    """
    
    def __init__(self, config: Dict):
        """Initialize RSI strategy."""
        super().__init__("RSI", config)
        self.period = config.get('period', 14)
        self.oversold = config.get('oversold', 30)
        self.overbought = config.get('overbought', 70)
    
    def calculate_rsi(self, df: pd.DataFrame) -> pd.Series:
        """Calculate RSI indicator."""
        delta = df['close'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI."""
        df = df.copy()
        df['rsi'] = self.calculate_rsi(df)
        return df
    
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Analyze data and generate signal.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Trading signal
        """
        if len(df) < self.period + 1:
            logger.warning(f"Not enough data for RSI strategy (need {self.period + 1}, have {len(df)})")
            return Signal.HOLD
        
        # Calculate indicators
        df = self.get_indicators(df)
        
        # Get current RSI
        current_rsi = df.iloc[-1]['rsi']
        
        if pd.isna(current_rsi):
            return Signal.HOLD
        
        # Oversold condition (potential buy)
        if current_rsi < self.oversold:
            logger.info(f"RSI Strategy: Oversold condition (RSI={current_rsi:.2f})")
            return Signal.BUY
        
        # Overbought condition (potential sell)
        if current_rsi > self.overbought:
            logger.info(f"RSI Strategy: Overbought condition (RSI={current_rsi:.2f})")
            return Signal.SELL
        
        return Signal.HOLD
