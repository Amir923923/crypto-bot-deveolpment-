"""
Main crypto trading bot implementation.
"""

import time
import pandas as pd
from typing import Dict, List
from datetime import datetime

from src.config import get_config
from src.utils.logger import setup_logger, get_logger
from src.exchange.exchange_interface import ExchangeInterface
from src.strategies.moving_average_strategy import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.bollinger_bands_strategy import BollingerBandsStrategy
from src.strategies.base_strategy import Signal, BaseStrategy
from src.risk.risk_manager import RiskManager


class CryptoBot:
    """Main trading bot orchestrator."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the crypto trading bot.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = get_config(config_path)
        
        # Setup logging
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get('logging.file_path', 'logs/crypto_bot.log')
        self.logger = setup_logger(log_level, log_file)
        
        self.logger.info("=" * 60)
        self.logger.info("Initializing Crypto Trading Bot")
        self.logger.info("=" * 60)
        
        # Initialize exchange
        self.exchange = ExchangeInterface(
            exchange_name=self.config.exchange_name,
            api_key=self.config.api_key,
            api_secret=self.config.api_secret,
            testnet=self.config.get('exchange.testnet', True)
        )
        
        # Initialize risk manager
        risk_config = {
            'max_positions': self.config.get('trading.max_positions', 3),
            'stop_loss_percentage': self.config.get('trading.stop_loss_percentage', 2.0),
            'take_profit_percentage': self.config.get('trading.take_profit_percentage', 5.0),
            'max_daily_loss': self.config.get('trading.max_daily_loss', 10.0),
            'trade_amount': self.config.get('trading.trade_amount', 100),
        }
        self.risk_manager = RiskManager(risk_config)
        
        # Initialize strategies
        self.strategies: List[BaseStrategy] = []
        self._initialize_strategies()
        
        # Trading configuration
        self.symbols = self.config.get('trading.symbols', ['BTC/USDT'])
        self.timeframe = self.config.get('trading.timeframe', '1h')
        self.lookback_periods = self.config.get('trading.lookback_periods', 100)
        self.base_currency = self.config.get('trading.base_currency', 'USDT')
        
        # Bot state
        self.running = False
        self.iteration_count = 0
        
        self.logger.info(f"Trading mode: {self.config.trading_mode}")
        self.logger.info(f"Symbols: {', '.join(self.symbols)}")
        self.logger.info(f"Timeframe: {self.timeframe}")
        self.logger.info(f"Strategies: {len(self.strategies)}")
    
    def _initialize_strategies(self):
        """Initialize trading strategies based on configuration."""
        strategies_config = self.config.get('strategies', {})
        
        # Moving Average Strategy
        ma_config = strategies_config.get('moving_average', {})
        if ma_config.get('enabled', False):
            self.strategies.append(MovingAverageStrategy(ma_config))
            self.logger.info("Enabled Moving Average strategy")
        
        # RSI Strategy
        rsi_config = strategies_config.get('rsi', {})
        if rsi_config.get('enabled', False):
            self.strategies.append(RSIStrategy(rsi_config))
            self.logger.info("Enabled RSI strategy")
        
        # Bollinger Bands Strategy
        bb_config = strategies_config.get('bollinger_bands', {})
        if bb_config.get('enabled', False):
            self.strategies.append(BollingerBandsStrategy(bb_config))
            self.logger.info("Enabled Bollinger Bands strategy")
    
    def fetch_market_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch and prepare market data for analysis.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, self.timeframe, self.lookback_periods)
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_symbol(self, symbol: str, df: pd.DataFrame) -> str:
        """
        Analyze a symbol using all enabled strategies.
        
        Args:
            symbol: Trading pair symbol
            df: Market data DataFrame
            
        Returns:
            Aggregated signal (BUY, SELL, or HOLD)
        """
        if df.empty:
            return Signal.HOLD
        
        signals = []
        
        for strategy in self.strategies:
            if strategy.should_execute():
                try:
                    signal = strategy.analyze(df)
                    signals.append(signal)
                    self.logger.debug(f"{strategy.name} signal for {symbol}: {signal}")
                except Exception as e:
                    self.logger.error(f"Error in {strategy.name} for {symbol}: {e}")
        
        # Aggregate signals (simple majority voting)
        if not signals:
            return Signal.HOLD
        
        buy_count = signals.count(Signal.BUY)
        sell_count = signals.count(Signal.SELL)
        
        # Require at least 2 strategies to agree for a signal
        if buy_count >= 2:
            self.logger.info(f"Aggregated signal for {symbol}: BUY ({buy_count}/{len(signals)})")
            return Signal.BUY
        elif sell_count >= 2:
            self.logger.info(f"Aggregated signal for {symbol}: SELL ({sell_count}/{len(signals)})")
            return Signal.SELL
        
        return Signal.HOLD
    
    def execute_trade(self, symbol: str, signal: str, current_price: float):
        """
        Execute a trade based on the signal.
        
        Args:
            symbol: Trading pair symbol
            signal: Trading signal (BUY or SELL)
            current_price: Current market price
        """
        try:
            # Check if we already have a position
            has_position = self.risk_manager.has_open_position(symbol)
            
            if signal == Signal.BUY and not has_position:
                # Open long position
                if self.risk_manager.can_open_position():
                    # Get balance
                    balance = self._get_available_balance()
                    
                    # Calculate position size
                    amount = self.risk_manager.calculate_position_size(current_price, balance)
                    
                    if amount > 0:
                        if self.config.is_paper_trading:
                            self.logger.info(f"[PAPER] Would BUY {amount:.6f} {symbol} at {current_price:.2f}")
                            # Record position in risk manager
                            self.risk_manager.open_position(symbol, 'long', current_price, amount)
                        else:
                            # Execute real trade
                            order = self.exchange.create_market_order(symbol, 'buy', amount)
                            self.risk_manager.open_position(symbol, 'long', current_price, amount)
            
            elif signal == Signal.SELL and has_position:
                # Close long position
                position = self.risk_manager.get_position(symbol)
                if position and position.status == 'open':
                    if self.config.is_paper_trading:
                        self.logger.info(f"[PAPER] Would SELL {position.amount:.6f} {symbol} at {current_price:.2f}")
                        self.risk_manager.close_position(symbol, current_price)
                    else:
                        # Execute real trade
                        order = self.exchange.create_market_order(symbol, 'sell', position.amount)
                        self.risk_manager.close_position(symbol, current_price)
        
        except Exception as e:
            self.logger.error(f"Error executing trade for {symbol}: {e}")
    
    def _get_available_balance(self) -> float:
        """Get available balance for trading."""
        try:
            if self.config.is_paper_trading:
                # Return configured trade amount for paper trading
                return self.config.get('trading.trade_amount', 100)
            else:
                balance = self.exchange.fetch_balance()
                return balance['free'].get(self.base_currency, 0)
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return 0
    
    def run_iteration(self):
        """Run one iteration of the trading bot."""
        self.iteration_count += 1
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"Iteration #{self.iteration_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"{'=' * 60}")
        
        # Reset daily stats if needed
        self.risk_manager.reset_daily_stats()
        
        # Get current prices for position monitoring
        current_prices = {}
        
        for symbol in self.symbols:
            try:
                # Fetch market data
                self.logger.info(f"Analyzing {symbol}...")
                df = self.fetch_market_data(symbol)
                
                if df.empty:
                    self.logger.warning(f"No data available for {symbol}")
                    continue
                
                # Get current price
                current_price = df.iloc[-1]['close']
                current_prices[symbol] = current_price
                
                self.logger.info(f"{symbol} current price: {current_price:.2f}")
                
                # Analyze with strategies
                signal = self.analyze_symbol(symbol, df)
                
                # Execute trade if signal is not HOLD
                if signal != Signal.HOLD:
                    self.execute_trade(symbol, signal, current_price)
                else:
                    self.logger.info(f"No trade signal for {symbol}")
            
            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")
        
        # Check existing positions for stop loss / take profit
        self.risk_manager.check_positions(current_prices)
        
        # Display open positions
        open_positions = self.risk_manager.get_open_positions()
        if open_positions:
            self.logger.info(f"\nOpen positions: {len(open_positions)}")
            for symbol, position in open_positions.items():
                pnl = position.calculate_pnl(current_prices.get(symbol, position.entry_price))
                self.logger.info(f"  {symbol}: {position.side} | Entry: {position.entry_price:.2f} | "
                               f"Amount: {position.amount:.6f} | PnL: {pnl:.2f}")
        
        self.logger.info(f"Daily PnL: {self.risk_manager.daily_pnl:.2f}")
    
    def start(self, interval: int = 3600):
        """
        Start the trading bot.
        
        Args:
            interval: Time interval between iterations in seconds (default: 3600 = 1 hour)
        """
        self.running = True
        self.logger.info(f"Starting bot with {interval}s interval...")
        
        try:
            while self.running:
                try:
                    self.run_iteration()
                except Exception as e:
                    self.logger.error(f"Error in bot iteration: {e}", exc_info=True)
                
                # Wait for next iteration
                if self.running:
                    self.logger.info(f"Waiting {interval}s until next iteration...")
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the trading bot."""
        self.logger.info("Stopping bot...")
        self.running = False
        
        # Display final statistics
        open_positions = self.risk_manager.get_open_positions()
        total_pnl = self.risk_manager.get_total_pnl()
        
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info("Bot Statistics")
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"Total iterations: {self.iteration_count}")
        self.logger.info(f"Open positions: {len(open_positions)}")
        self.logger.info(f"Total PnL: {total_pnl:.2f}")
        self.logger.info(f"Daily PnL: {self.risk_manager.daily_pnl:.2f}")
        self.logger.info(f"{'=' * 60}")
        self.logger.info("Bot stopped successfully")
