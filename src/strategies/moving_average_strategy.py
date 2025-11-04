"""
Moving Average Crossover Strategy.
"""

import pandas as pd
from typing import Dict
from src.strategies.base_strategy import BaseStrategy, Signal
from src.utils.logger import get_logger

logger = get_logger()


class MovingAverageStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.
    
    Generates BUY signal when fast MA crosses above slow MA.
    Generates SELL signal when fast MA crosses below slow MA.
    """
    
    def __init__(self, config: Dict):
        """Initialize Moving Average strategy."""
        super().__init__("Moving Average", config)
        self.fast_period = config.get('fast_period', 10)
        self.slow_period = config.get('slow_period', 30)
    
    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages."""
        df = df.copy()
        df['ma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['ma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        return df
    
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Analyze data and generate signal.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Trading signal
        """
        if len(df) < self.slow_period:
            logger.warning(f"Not enough data for MA strategy (need {self.slow_period}, have {len(df)})")
            return Signal.HOLD
        
        # Calculate indicators
        df = self.get_indicators(df)
        
        # Get last two rows for crossover detection
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Check for crossover
        if pd.isna(current['ma_fast']) or pd.isna(current['ma_slow']):
            return Signal.HOLD
        
        # Bullish crossover (fast MA crosses above slow MA)
        if previous['ma_fast'] <= previous['ma_slow'] and current['ma_fast'] > current['ma_slow']:
            logger.info(f"MA Strategy: Bullish crossover detected (fast={current['ma_fast']:.2f}, slow={current['ma_slow']:.2f})")
            return Signal.BUY
        
        # Bearish crossover (fast MA crosses below slow MA)
        if previous['ma_fast'] >= previous['ma_slow'] and current['ma_fast'] < current['ma_slow']:
            logger.info(f"MA Strategy: Bearish crossover detected (fast={current['ma_fast']:.2f}, slow={current['ma_slow']:.2f})")
            return Signal.SELL
        
        return Signal.HOLD
