#!/usr/bin/env python3
"""
Demo script to showcase the crypto bot's capabilities without needing API keys.
This uses sample data to demonstrate strategies and risk management.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.bollinger_bands_strategy import BollingerBandsStrategy
from src.strategies.base_strategy import Signal
from src.risk.risk_manager import RiskManager
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger('INFO')


def generate_sample_data(periods=200, trend='bullish', volatility=0.02):
    """
    Generate sample market data for demonstration.
    
    Args:
        periods: Number of data points
        trend: 'bullish', 'bearish', or 'sideways'
        volatility: Price volatility
    
    Returns:
        DataFrame with OHLCV data
    """
    # Constants for trend calculation
    SIDEWAYS_CYCLES = 4
    SIDEWAYS_AMPLITUDE = 5
    
    np.random.seed(42)
    
    # Generate base price trend
    if trend == 'bullish':
        trend_component = np.linspace(0, 20, periods)
    elif trend == 'bearish':
        trend_component = np.linspace(0, -20, periods)
    else:  # sideways
        trend_component = np.sin(np.linspace(0, SIDEWAYS_CYCLES * np.pi, periods)) * SIDEWAYS_AMPLITUDE
    
    # Generate random walk
    random_walk = np.cumsum(np.random.randn(periods) * volatility)
    
    # Combine components
    base_price = 50000
    close_prices = base_price + trend_component * 100 + random_walk * 100
    
    # Generate OHLCV data
    dates = pd.date_range(start=datetime.now() - timedelta(hours=periods), periods=periods, freq='1h')
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(periods) * 50,
        'high': close_prices + abs(np.random.randn(periods) * 100),
        'low': close_prices - abs(np.random.randn(periods) * 100),
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, periods)
    })
    
    df.set_index('timestamp', inplace=True)
    
    return df


def demo_strategies():
    """Demonstrate trading strategies with sample data."""
    logger.info("=" * 70)
    logger.info("CRYPTO BOT DEMO - TRADING STRATEGIES")
    logger.info("=" * 70)
    
    # Generate sample data for different market conditions
    scenarios = [
        ('Bullish Market', 'bullish'),
        ('Bearish Market', 'bearish'),
        ('Sideways Market', 'sideways')
    ]
    
    for scenario_name, trend in scenarios:
        logger.info(f"\n{'-' * 70}")
        logger.info(f"Scenario: {scenario_name}")
        logger.info(f"{'-' * 70}")
        
        # Generate data
        df = generate_sample_data(periods=200, trend=trend)
        current_price = df.iloc[-1]['close']
        
        logger.info(f"Current Price: ${current_price:.2f}")
        logger.info(f"Price Range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        logger.info(f"Average Volume: {df['volume'].mean():.0f}")
        
        # Initialize strategies
        ma_strategy = MovingAverageStrategy({'enabled': True, 'fast_period': 10, 'slow_period': 30})
        rsi_strategy = RSIStrategy({'enabled': True, 'period': 14, 'oversold': 30, 'overbought': 70})
        bb_strategy = BollingerBandsStrategy({'enabled': True, 'period': 20, 'std_dev': 2})
        
        strategies = [ma_strategy, rsi_strategy, bb_strategy]
        
        # Analyze with each strategy
        logger.info("\nStrategy Analysis:")
        signals = []
        
        for strategy in strategies:
            signal = strategy.analyze(df)
            signals.append(signal)
            
            # Get indicator values
            df_indicators = strategy.get_indicators(df)
            last_row = df_indicators.iloc[-1]
            
            logger.info(f"  {strategy.name}: {signal}")
            
            # Show specific indicator values
            if isinstance(strategy, MovingAverageStrategy):
                logger.info(f"    - Fast MA: ${last_row['ma_fast']:.2f}")
                logger.info(f"    - Slow MA: ${last_row['ma_slow']:.2f}")
            elif isinstance(strategy, RSIStrategy):
                logger.info(f"    - RSI: {last_row['rsi']:.2f}")
            elif isinstance(strategy, BollingerBandsStrategy):
                logger.info(f"    - Upper Band: ${last_row['bb_upper']:.2f}")
                logger.info(f"    - Middle Band: ${last_row['bb_middle']:.2f}")
                logger.info(f"    - Lower Band: ${last_row['bb_lower']:.2f}")
        
        # Aggregate signals
        buy_count = signals.count(Signal.BUY)
        sell_count = signals.count(Signal.SELL)
        hold_count = signals.count(Signal.HOLD)
        
        logger.info(f"\nSignal Summary:")
        logger.info(f"  BUY: {buy_count}, SELL: {sell_count}, HOLD: {hold_count}")
        
        if buy_count >= 2:
            logger.info(f"  → AGGREGATED SIGNAL: BUY 🟢")
        elif sell_count >= 2:
            logger.info(f"  → AGGREGATED SIGNAL: SELL 🔴")
        else:
            logger.info(f"  → AGGREGATED SIGNAL: HOLD ⚪")


def demo_risk_management():
    """Demonstrate risk management features."""
    logger.info("\n\n" + "=" * 70)
    logger.info("CRYPTO BOT DEMO - RISK MANAGEMENT")
    logger.info("=" * 70)
    
    # Initialize risk manager
    config = {
        'max_positions': 3,
        'stop_loss_percentage': 2.0,
        'take_profit_percentage': 5.0,
        'max_daily_loss': 10.0,
        'trade_amount': 1000,
    }
    
    risk_manager = RiskManager(config)
    
    logger.info(f"\nRisk Management Configuration:")
    logger.info(f"  Max Positions: {config['max_positions']}")
    logger.info(f"  Stop Loss: {config['stop_loss_percentage']}%")
    logger.info(f"  Take Profit: {config['take_profit_percentage']}%")
    logger.info(f"  Max Daily Loss: {config['max_daily_loss']}%")
    logger.info(f"  Trade Amount: ${config['trade_amount']}")
    
    # Simulate opening positions
    logger.info("\n" + "-" * 70)
    logger.info("Simulating Trading Positions")
    logger.info("-" * 70)
    
    # Position 1: Profitable trade
    logger.info("\n1. Opening BTC/USDT position")
    entry_price = 50000
    amount = 0.02
    position1 = risk_manager.open_position('BTC/USDT', 'long', entry_price, amount)
    logger.info(f"   Entry: ${entry_price:.2f}")
    logger.info(f"   Amount: {amount} BTC")
    logger.info(f"   Stop Loss: ${position1.stop_loss:.2f}")
    logger.info(f"   Take Profit: ${position1.take_profit:.2f}")
    
    # Simulate price increase - take profit triggered
    new_price = 52600
    logger.info(f"\n   Price moved to ${new_price:.2f}")
    if position1.should_take_profit(new_price):
        risk_manager.close_position('BTC/USDT', new_price)
        logger.info(f"   ✅ Take Profit triggered!")
        logger.info(f"   PnL: ${position1.pnl:.2f}")
    
    # Position 2: Loss trade
    logger.info("\n2. Opening ETH/USDT position")
    entry_price = 3000
    amount = 0.33
    position2 = risk_manager.open_position('ETH/USDT', 'long', entry_price, amount)
    logger.info(f"   Entry: ${entry_price:.2f}")
    logger.info(f"   Amount: {amount} ETH")
    logger.info(f"   Stop Loss: ${position2.stop_loss:.2f}")
    logger.info(f"   Take Profit: ${position2.take_profit:.2f}")
    
    # Simulate price decrease - stop loss triggered
    new_price = 2930
    logger.info(f"\n   Price moved to ${new_price:.2f}")
    if position2.should_stop_loss(new_price):
        risk_manager.close_position('ETH/USDT', new_price)
        logger.info(f"   🛑 Stop Loss triggered!")
        logger.info(f"   PnL: ${position2.pnl:.2f}")
    
    # Summary
    logger.info("\n" + "-" * 70)
    logger.info("Trading Summary")
    logger.info("-" * 70)
    logger.info(f"Total Positions: {len(risk_manager.positions)}")
    logger.info(f"Open Positions: {len(risk_manager.get_open_positions())}")
    logger.info(f"Total PnL: ${risk_manager.get_total_pnl():.2f}")
    logger.info(f"Daily PnL: ${risk_manager.daily_pnl:.2f}")


def main():
    """Run the demo."""
    logger.info("\n\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 15 + "CRYPTO TRADING BOT DEMONSTRATION" + " " * 21 + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("\nThis demo showcases the bot's capabilities using simulated data.")
    logger.info("No API keys or real trading required!\n")
    
    try:
        # Demo 1: Trading Strategies
        demo_strategies()
        
        # Demo 2: Risk Management
        demo_risk_management()
        
        logger.info("\n\n" + "=" * 70)
        logger.info("DEMO COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info("\nNext Steps:")
        logger.info("  1. Review the code in src/ to understand how it works")
        logger.info("  2. Configure config.yaml for your trading preferences")
        logger.info("  3. Run 'python main.py --once' to test with real data")
        logger.info("  4. Start with paper trading before using real money")
        logger.info("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
