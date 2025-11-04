"""
Arbitrage opportunity detection logic.
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity between two exchanges."""
    buy_exchange: str
    sell_exchange: str
    symbol: str
    buy_price: float
    sell_price: float
    profit_percentage: float
    spread: float
    timestamp: float
    
    def __str__(self):
        return (f"Arbitrage: Buy {self.symbol} on {self.buy_exchange} @ {self.buy_price:.2f}, "
                f"Sell on {self.sell_exchange} @ {self.sell_price:.2f} | "
                f"Profit: {self.profit_percentage:.2f}% (${self.spread:.2f})")


class ArbitrageDetector:
    """Detects arbitrage opportunities across multiple exchanges."""
    
    def __init__(self, exchange_manager):
        """
        Initialize the arbitrage detector.
        
        Args:
            exchange_manager: ExchangeManager instance
        """
        self.exchange_manager = exchange_manager
        self.min_profit = Config.MIN_PROFIT_PERCENTAGE
    
    def calculate_profit_percentage(self, buy_price: float, sell_price: float) -> float:
        """
        Calculate profit percentage accounting for fees.
        
        Args:
            buy_price: Price to buy at
            sell_price: Price to sell at
            
        Returns:
            Profit percentage after estimated fees
        """
        if buy_price <= 0:
            return 0.0
        
        gross_profit = ((sell_price - buy_price) / buy_price) * 100
        net_profit = gross_profit - Config.TRADING_FEE_PERCENTAGE
        
        return net_profit
    
    def calculate_spread(self, buy_price: float, sell_price: float, 
                        trade_amount: float) -> float:
        """
        Calculate absolute spread in USD.
        
        Args:
            buy_price: Price to buy at
            sell_price: Price to sell at
            trade_amount: Amount to trade in USD
            
        Returns:
            Absolute profit in USD
        """
        if buy_price <= 0:
            return 0.0
        
        quantity = trade_amount / buy_price
        revenue = quantity * sell_price
        cost = trade_amount
        
        # Account for fees (0.1% per transaction)
        fees = (cost + revenue) * 0.001
        
        return revenue - cost - fees
    
    def find_opportunities(self, symbol: str) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities for a given trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            List of arbitrage opportunities
        """
        tickers = self.exchange_manager.get_all_tickers(symbol)
        
        if len(tickers) < 2:
            logger.debug(f"Not enough exchanges have data for {symbol}")
            return []
        
        opportunities = []
        
        # Compare all exchange pairs
        exchanges = list(tickers.keys())
        for i, buy_exchange in enumerate(exchanges):
            for sell_exchange in exchanges[i+1:]:
                # Check both directions
                opportunities.extend(self._check_opportunity(
                    symbol, buy_exchange, sell_exchange, tickers
                ))
                opportunities.extend(self._check_opportunity(
                    symbol, sell_exchange, buy_exchange, tickers
                ))
        
        return opportunities
    
    def _check_opportunity(self, symbol: str, buy_exchange: str, 
                          sell_exchange: str, tickers: Dict) -> List[ArbitrageOpportunity]:
        """
        Check for arbitrage opportunity between two exchanges.
        
        Args:
            symbol: Trading pair symbol
            buy_exchange: Exchange to buy from
            sell_exchange: Exchange to sell on
            tickers: Dictionary of ticker data
            
        Returns:
            List containing opportunity if profitable, empty otherwise
        """
        opportunities = []
        
        buy_ticker = tickers.get(buy_exchange)
        sell_ticker = tickers.get(sell_exchange)
        
        if not buy_ticker or not sell_ticker:
            return opportunities
        
        # Get ask price (buy) and bid price (sell)
        buy_price = buy_ticker.get('ask')
        sell_price = sell_ticker.get('bid')
        
        if not buy_price or not sell_price or buy_price <= 0 or sell_price <= 0:
            return opportunities
        
        profit_percentage = self.calculate_profit_percentage(buy_price, sell_price)
        
        if profit_percentage >= self.min_profit:
            spread = self.calculate_spread(buy_price, sell_price, Config.TRADE_AMOUNT_USD)
            
            opportunity = ArbitrageOpportunity(
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                symbol=symbol,
                buy_price=buy_price,
                sell_price=sell_price,
                profit_percentage=profit_percentage,
                spread=spread,
                timestamp=buy_ticker.get('timestamp', 0)
            )
            
            opportunities.append(opportunity)
            logger.info(f"Found opportunity: {opportunity}")
        
        return opportunities
    
    def scan_all_pairs(self) -> List[ArbitrageOpportunity]:
        """
        Scan all configured trading pairs for arbitrage opportunities.
        
        Returns:
            List of all found arbitrage opportunities
        """
        all_opportunities = []
        
        for symbol in Config.TRADING_PAIRS:
            try:
                opportunities = self.find_opportunities(symbol)
                all_opportunities.extend(opportunities)
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        return all_opportunities
