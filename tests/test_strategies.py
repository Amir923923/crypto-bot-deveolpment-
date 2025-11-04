"""
Tests for trading strategies.
"""

import pytest
import pandas as pd
import numpy as np
from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.bollinger_bands_strategy import BollingerBandsStrategy
from src.strategies.base_strategy import Signal


@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    np.random.seed(42)
    
    # Generate realistic price data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(100) * 0.5,
        'high': close_prices + abs(np.random.randn(100) * 1),
        'low': close_prices - abs(np.random.randn(100) * 1),
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    return df


class TestMovingAverageStrategy:
    """Test Moving Average Strategy."""
    
    def test_initialization(self):
        """Test strategy initialization."""
        config = {'enabled': True, 'fast_period': 10, 'slow_period': 30}
        strategy = MovingAverageStrategy(config)
        
        assert strategy.name == "Moving Average"
        assert strategy.fast_period == 10
        assert strategy.slow_period == 30
        assert strategy.enabled is True
    
    def test_indicators_calculation(self, sample_data):
        """Test moving average calculation."""
        config = {'enabled': True, 'fast_period': 10, 'slow_period': 30}
        strategy = MovingAverageStrategy(config)
        
        df = strategy.get_indicators(sample_data)
        
        assert 'ma_fast' in df.columns
        assert 'ma_slow' in df.columns
        assert not df['ma_fast'].iloc[-1] is pd.NA
        assert not df['ma_slow'].iloc[-1] is pd.NA
    
    def test_signal_generation(self, sample_data):
        """Test signal generation."""
        config = {'enabled': True, 'fast_period': 10, 'slow_period': 30}
        strategy = MovingAverageStrategy(config)
        
        signal = strategy.analyze(sample_data)
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
    
    def test_insufficient_data(self):
        """Test with insufficient data."""
        config = {'enabled': True, 'fast_period': 10, 'slow_period': 30}
        strategy = MovingAverageStrategy(config)
        
        # Create small dataset
        df = pd.DataFrame({
            'close': [100, 101, 102]
        })
        
        signal = strategy.analyze(df)
        assert signal == Signal.HOLD


class TestRSIStrategy:
    """Test RSI Strategy."""
    
    def test_initialization(self):
        """Test strategy initialization."""
        config = {'enabled': True, 'period': 14, 'oversold': 30, 'overbought': 70}
        strategy = RSIStrategy(config)
        
        assert strategy.name == "RSI"
        assert strategy.period == 14
        assert strategy.oversold == 30
        assert strategy.overbought == 70
    
    def test_rsi_calculation(self, sample_data):
        """Test RSI calculation."""
        config = {'enabled': True, 'period': 14, 'oversold': 30, 'overbought': 70}
        strategy = RSIStrategy(config)
        
        df = strategy.get_indicators(sample_data)
        
        assert 'rsi' in df.columns
        rsi_value = df['rsi'].iloc[-1]
        assert not pd.isna(rsi_value)
        assert 0 <= rsi_value <= 100
    
    def test_signal_generation(self, sample_data):
        """Test signal generation."""
        config = {'enabled': True, 'period': 14, 'oversold': 30, 'overbought': 70}
        strategy = RSIStrategy(config)
        
        signal = strategy.analyze(sample_data)
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]


class TestBollingerBandsStrategy:
    """Test Bollinger Bands Strategy."""
    
    def test_initialization(self):
        """Test strategy initialization."""
        config = {'enabled': True, 'period': 20, 'std_dev': 2}
        strategy = BollingerBandsStrategy(config)
        
        assert strategy.name == "Bollinger Bands"
        assert strategy.period == 20
        assert strategy.std_dev == 2
    
    def test_bands_calculation(self, sample_data):
        """Test Bollinger Bands calculation."""
        config = {'enabled': True, 'period': 20, 'std_dev': 2}
        strategy = BollingerBandsStrategy(config)
        
        df = strategy.get_indicators(sample_data)
        
        assert 'bb_middle' in df.columns
        assert 'bb_upper' in df.columns
        assert 'bb_lower' in df.columns
        
        # Upper band should be above middle, middle above lower
        last_row = df.iloc[-1]
        assert last_row['bb_upper'] > last_row['bb_middle']
        assert last_row['bb_middle'] > last_row['bb_lower']
    
    def test_signal_generation(self, sample_data):
        """Test signal generation."""
        config = {'enabled': True, 'period': 20, 'std_dev': 2}
        strategy = BollingerBandsStrategy(config)
        
        signal = strategy.analyze(sample_data)
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
