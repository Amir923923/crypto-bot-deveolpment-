"""
Helper utilities for the crypto trading bot.
"""

from typing import Dict, List, Any
import pandas as pd
from datetime import datetime


def format_price(price: float, decimals: int = 2) -> str:
    """
    Format price for display.
    
    Args:
        price: Price value
        decimals: Number of decimal places
        
    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"


def format_percentage(value: float) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0.05 = 5%)
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.2f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def validate_symbol(symbol: str) -> bool:
    """
    Validate trading pair symbol format.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT')
        
    Returns:
        True if valid, False otherwise
    """
    if '/' not in symbol:
        return False
    
    parts = symbol.split('/')
    if len(parts) != 2:
        return False
    
    # Check if both parts are non-empty
    return all(len(part) > 0 for part in parts)


def parse_timeframe(timeframe: str) -> int:
    """
    Parse timeframe string to seconds.
    
    Args:
        timeframe: Timeframe string (e.g., '1m', '5m', '1h', '1d')
        
    Returns:
        Timeframe in seconds
    """
    timeframe_map = {
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800,
    }
    
    if len(timeframe) < 2:
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    try:
        value = int(timeframe[:-1])
    except ValueError:
        raise ValueError(f"Invalid timeframe format: {timeframe}. Expected format like '1h', '5m', etc.")
    
    unit = timeframe[-1]
    
    if unit not in timeframe_map:
        raise ValueError(f"Invalid timeframe unit: {unit}")
    
    return value * timeframe_map[unit]


def ohlcv_to_dataframe(ohlcv: List[List], add_indicators: bool = False) -> pd.DataFrame:
    """
    Convert OHLCV data to pandas DataFrame.
    
    Args:
        ohlcv: List of OHLCV data [timestamp, open, high, low, close, volume]
        add_indicators: Whether to add basic indicators
        
    Returns:
        DataFrame with OHLCV data
    """
    df = pd.DataFrame(
        ohlcv,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    if add_indicators:
        # Add basic indicators
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
    
    return df


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sharpe ratio for a series of returns.
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (default: 0)
        
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0.0


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown from a series of prices.
    
    Args:
        prices: Series of prices
        
    Returns:
        Maximum drawdown as a percentage
    """
    cumulative_returns = (1 + prices.pct_change()).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    return drawdown.min()


def is_market_hours(exchange: str = 'binance') -> bool:
    """
    Check if market is open (crypto markets are 24/7).
    
    Args:
        exchange: Exchange name
        
    Returns:
        Always True for crypto markets
    """
    # Crypto markets are 24/7
    return True


def round_to_precision(value: float, precision: int) -> float:
    """
    Round value to specified precision.
    
    Args:
        value: Value to round
        precision: Number of decimal places
        
    Returns:
        Rounded value
    """
    return round(value, precision)


def get_timestamp() -> int:
    """
    Get current timestamp in milliseconds.
    
    Returns:
        Current timestamp
    """
    return int(datetime.now().timestamp() * 1000)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    return numerator / denominator if denominator != 0 else default
