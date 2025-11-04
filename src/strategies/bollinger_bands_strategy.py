"""
Bollinger Bands Strategy.
"""

import pandas as pd
from typing import Dict
from src.strategies.base_strategy import BaseStrategy, Signal
from src.utils.logger import get_logger

logger = get_logger()


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy.
    
    Generates BUY signal when price touches lower band.
    Generates SELL signal when price touches upper band.
    """
    
    def __init__(self, config: Dict):
        """Initialize Bollinger Bands strategy."""
        super().__init__("Bollinger Bands", config)
        self.period = config.get('period', 20)
        self.std_dev = config.get('std_dev', 2)
    
    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        df = df.copy()
        
        # Calculate middle band (SMA)
        df['bb_middle'] = df['close'].rolling(window=self.period).mean()
        
        # Calculate standard deviation
        df['bb_std'] = df['close'].rolling(window=self.period).std()
        
        # Calculate upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * self.std_dev)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * self.std_dev)
        
        return df
    
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Analyze data and generate signal.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Trading signal
        """
        if len(df) < self.period:
            logger.warning(f"Not enough data for BB strategy (need {self.period}, have {len(df)})")
            return Signal.HOLD
        
        # Calculate indicators
        df = self.get_indicators(df)
        
        # Get current values
        current = df.iloc[-1]
        current_price = current['close']
        
        if pd.isna(current['bb_upper']) or pd.isna(current['bb_lower']):
            return Signal.HOLD
        
        # Price touches or goes below lower band (oversold)
        if current_price <= current['bb_lower']:
            logger.info(f"BB Strategy: Price at lower band (price={current_price:.2f}, lower={current['bb_lower']:.2f})")
            return Signal.BUY
        
        # Price touches or goes above upper band (overbought)
        if current_price >= current['bb_upper']:
            logger.info(f"BB Strategy: Price at upper band (price={current_price:.2f}, upper={current['bb_upper']:.2f})")
            return Signal.SELL
        
        return Signal.HOLD
