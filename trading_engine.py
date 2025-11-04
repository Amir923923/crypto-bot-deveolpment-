"""
Trading execution engine for the arbitrage bot.
"""
import logging
import time
from typing import Optional
from arbitrage_detector import ArbitrageOpportunity
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingEngine:
    """Executes arbitrage trades with safety checks."""
    
    def __init__(self, exchange_manager):
        """
        Initialize the trading engine.
        
        Args:
            exchange_manager: ExchangeManager instance
        """
        self.exchange_manager = exchange_manager
        self.trade_history = []
    
    def validate_opportunity(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Validate an arbitrage opportunity before execution.
        
        Args:
            opportunity: ArbitrageOpportunity to validate
            
        Returns:
            True if opportunity is still valid, False otherwise
        """
        # Re-fetch current prices
        buy_ticker = self.exchange_manager.get_ticker(
            opportunity.buy_exchange, opportunity.symbol
        )
        sell_ticker = self.exchange_manager.get_ticker(
            opportunity.sell_exchange, opportunity.symbol
        )
        
        if not buy_ticker or not sell_ticker:
            logger.warning("Could not fetch current prices for validation")
            return False
        
        current_buy_price = buy_ticker.get('ask')
        current_sell_price = sell_ticker.get('bid')
        
        if not current_buy_price or not current_sell_price:
            return False
        
        # Check if opportunity still exists with slippage tolerance
        price_movement = abs(current_buy_price - opportunity.buy_price) / opportunity.buy_price * 100
        
        if price_movement > Config.MAX_SLIPPAGE_PERCENTAGE:
            logger.warning(f"Price moved too much: {price_movement:.2f}%")
            return False
        
        # Recalculate profit with current prices
        gross_profit = ((current_sell_price - current_buy_price) / current_buy_price) * 100
        net_profit = gross_profit - 0.2  # Account for fees
        
        if net_profit < Config.MIN_PROFIT_PERCENTAGE:
            logger.warning(f"Profit dropped below threshold: {net_profit:.2f}%")
            return False
        
        return True
    
    def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Execute an arbitrage trade.
        
        Args:
            opportunity: ArbitrageOpportunity to execute
            
        Returns:
            True if execution successful, False otherwise
        """
        logger.info(f"Attempting to execute: {opportunity}")
        
        # Validate opportunity is still valid
        if not self.validate_opportunity(opportunity):
            logger.warning("Opportunity validation failed, skipping execution")
            return False
        
        # Calculate trade amount
        trade_amount_usd = Config.TRADE_AMOUNT_USD
        quantity = trade_amount_usd / opportunity.buy_price
        
        if Config.DRY_RUN:
            logger.info(f"[DRY RUN] Would execute arbitrage:")
            logger.info(f"  1. Buy {quantity:.6f} {opportunity.symbol} on {opportunity.buy_exchange} @ {opportunity.buy_price}")
            logger.info(f"  2. Sell {quantity:.6f} {opportunity.symbol} on {opportunity.sell_exchange} @ {opportunity.sell_price}")
            logger.info(f"  Expected profit: ${opportunity.spread:.2f} ({opportunity.profit_percentage:.2f}%)")
            
            self.trade_history.append({
                'opportunity': opportunity,
                'quantity': quantity,
                'status': 'dry_run',
                'timestamp': time.time()
            })
            return True
        
        # Execute buy order
        logger.info(f"Placing buy order on {opportunity.buy_exchange}")
        buy_order = self.exchange_manager.place_order(
            opportunity.buy_exchange,
            opportunity.symbol,
            'market',
            'buy',
            quantity
        )
        
        if not buy_order:
            logger.error("Buy order failed")
            return False
        
        # Execute sell order
        logger.info(f"Placing sell order on {opportunity.sell_exchange}")
        sell_order = self.exchange_manager.place_order(
            opportunity.sell_exchange,
            opportunity.symbol,
            'market',
            'sell',
            quantity
        )
        
        if not sell_order:
            logger.error("Sell order failed - manual intervention may be required!")
            # Note: In production, implement proper error handling and rollback
            return False
        
        logger.info("Arbitrage executed successfully!")
        
        self.trade_history.append({
            'opportunity': opportunity,
            'quantity': quantity,
            'buy_order': buy_order,
            'sell_order': sell_order,
            'status': 'executed',
            'timestamp': time.time()
        })
        
        return True
    
    def get_trade_history(self) -> list:
        """
        Get trading history.
        
        Returns:
            List of executed trades
        """
        return self.trade_history
    
    def get_total_profit(self) -> float:
        """
        Calculate total profit from all trades.
        
        Returns:
            Total profit in USD
        """
        total = 0.0
        for trade in self.trade_history:
            if 'opportunity' in trade:
                total += trade['opportunity'].spread
        return total
