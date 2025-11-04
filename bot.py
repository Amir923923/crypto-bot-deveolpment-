#!/usr/bin/env python3
"""
Main crypto arbitrage bot application.
"""
import time
import logging
import signal
import sys
from config import Config
from exchange_manager import ExchangeManager
from arbitrage_detector import ArbitrageDetector
from trading_engine import TradingEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArbitrageBot:
    """Main arbitrage bot controller."""
    
    def __init__(self):
        """Initialize the arbitrage bot."""
        self.running = False
        
        # Validate configuration
        Config.validate()
        
        # Initialize components
        logger.info("Initializing Crypto Arbitrage Bot...")
        self.exchange_manager = ExchangeManager()
        self.arbitrage_detector = ArbitrageDetector(self.exchange_manager)
        self.trading_engine = TradingEngine(self.exchange_manager)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Bot initialized successfully")
        self._print_configuration()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received, stopping bot...")
        self.running = False
    
    def _print_configuration(self):
        """Print current bot configuration."""
        logger.info("=" * 60)
        logger.info("Bot Configuration:")
        logger.info(f"  Mode: {'DRY RUN' if Config.DRY_RUN else 'LIVE TRADING'}")
        logger.info(f"  Min Profit: {Config.MIN_PROFIT_PERCENTAGE}%")
        logger.info(f"  Trade Amount: ${Config.TRADE_AMOUNT_USD}")
        logger.info(f"  Check Interval: {Config.CHECK_INTERVAL_SECONDS}s")
        logger.info(f"  Trading Pairs: {', '.join(Config.TRADING_PAIRS)}")
        logger.info(f"  Exchanges: {', '.join(Config.EXCHANGES)}")
        logger.info("=" * 60)
    
    def scan_once(self):
        """Perform a single scan for arbitrage opportunities."""
        logger.info("Scanning for arbitrage opportunities...")
        
        try:
            opportunities = self.arbitrage_detector.scan_all_pairs()
            
            if not opportunities:
                logger.info("No arbitrage opportunities found")
                return
            
            logger.info(f"Found {len(opportunities)} arbitrage opportunity(ies)")
            
            # Sort by profit percentage (highest first)
            opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
            
            # Execute the best opportunity
            best_opportunity = opportunities[0]
            logger.info(f"Best opportunity: {best_opportunity}")
            
            # Execute trade
            success = self.trading_engine.execute_arbitrage(best_opportunity)
            
            if success:
                logger.info("Trade executed successfully!")
            else:
                logger.warning("Trade execution failed")
                
        except Exception as e:
            logger.error(f"Error during scan: {e}", exc_info=True)
    
    def run(self):
        """Run the bot continuously."""
        self.running = True
        logger.info("Starting bot main loop...")
        
        scan_count = 0
        
        try:
            while self.running:
                scan_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Scan #{scan_count}")
                logger.info(f"{'='*60}")
                
                self.scan_once()
                
                # Print summary
                trade_history = self.trading_engine.get_trade_history()
                if trade_history:
                    total_profit = self.trading_engine.get_total_profit()
                    logger.info(f"Total trades executed: {len(trade_history)}")
                    logger.info(f"Total profit: ${total_profit:.2f}")
                
                if self.running:
                    logger.info(f"Waiting {Config.CHECK_INTERVAL_SECONDS} seconds until next scan...\n")
                    time.sleep(Config.CHECK_INTERVAL_SECONDS)
                    
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Cleanup and shutdown the bot."""
        logger.info("Shutting down bot...")
        
        # Print final statistics
        trade_history = self.trading_engine.get_trade_history()
        if trade_history:
            total_profit = self.trading_engine.get_total_profit()
            logger.info("=" * 60)
            logger.info("Final Statistics:")
            logger.info(f"  Total scans performed: N/A")
            logger.info(f"  Total trades executed: {len(trade_history)}")
            logger.info(f"  Total profit: ${total_profit:.2f}")
            logger.info("=" * 60)
        
        logger.info("Bot shutdown complete")


def main():
    """Main entry point."""
    logger.info("Crypto Arbitrage Bot v1.0")
    logger.info("=" * 60)
    
    try:
        bot = ArbitrageBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
