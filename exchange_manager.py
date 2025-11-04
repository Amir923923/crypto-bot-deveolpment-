"""
Exchange manager for handling multiple exchange connections and operations.
"""
import ccxt
import logging
from typing import Dict, List, Optional, Tuple
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExchangeManager:
    """Manages connections to multiple cryptocurrency exchanges."""
    
    def __init__(self):
        """Initialize exchange connections."""
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """Initialize exchange instances based on configuration."""
        for exchange_name in Config.EXCHANGES:
            try:
                exchange_class = getattr(ccxt, exchange_name)
                
                # Initialize exchange with or without API keys
                config = {'enableRateLimit': True}
                
                if exchange_name == 'binance' and Config.BINANCE_API_KEY:
                    config['apiKey'] = Config.BINANCE_API_KEY
                    config['secret'] = Config.BINANCE_SECRET
                elif exchange_name == 'kraken' and Config.KRAKEN_API_KEY:
                    config['apiKey'] = Config.KRAKEN_API_KEY
                    config['secret'] = Config.KRAKEN_SECRET
                
                self.exchanges[exchange_name] = exchange_class(config)
                logger.info(f"Initialized {exchange_name} exchange")
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_name}: {e}")
    
    def get_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """
        Get ticker information for a symbol from a specific exchange.
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Ticker dictionary or None if failed
        """
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None
        
        try:
            ticker = self.exchanges[exchange_name].fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Failed to fetch ticker for {symbol} on {exchange_name}: {e}")
            return None
    
    def get_all_tickers(self, symbol: str) -> Dict[str, Dict]:
        """
        Get ticker information for a symbol from all exchanges.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Dictionary mapping exchange names to ticker data
        """
        tickers = {}
        for exchange_name in self.exchanges:
            ticker = self.get_ticker(exchange_name, symbol)
            if ticker:
                tickers[exchange_name] = ticker
        return tickers
    
    def get_order_book(self, exchange_name: str, symbol: str, limit: int = 5) -> Optional[Dict]:
        """
        Get order book for a symbol from a specific exchange.
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            limit: Number of orders to fetch
            
        Returns:
            Order book dictionary or None if failed
        """
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None
        
        try:
            order_book = self.exchanges[exchange_name].fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            logger.error(f"Failed to fetch order book for {symbol} on {exchange_name}: {e}")
            return None
    
    def place_order(self, exchange_name: str, symbol: str, order_type: str, 
                   side: str, amount: float, price: Optional[float] = None) -> Optional[Dict]:
        """
        Place an order on an exchange.
        
        Args:
            exchange_name: Name of the exchange
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            order_type: 'market' or 'limit'
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Price for limit orders
            
        Returns:
            Order information or None if failed
        """
        if Config.DRY_RUN:
            logger.info(f"[DRY RUN] Would place {side} order for {amount} {symbol} on {exchange_name}")
            return {'id': 'dry_run', 'status': 'simulated'}
        
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None
        
        try:
            if order_type == 'market':
                order = self.exchanges[exchange_name].create_market_order(symbol, side, amount)
            else:
                if price is None:
                    logger.error("Price required for limit orders")
                    return None
                order = self.exchanges[exchange_name].create_limit_order(symbol, side, amount, price)
            
            logger.info(f"Order placed successfully on {exchange_name}: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Failed to place order on {exchange_name}: {e}")
            return None
    
    def get_balance(self, exchange_name: str) -> Optional[Dict]:
        """
        Get account balance from an exchange.
        
        Args:
            exchange_name: Name of the exchange
            
        Returns:
            Balance dictionary or None if failed
        """
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not initialized")
            return None
        
        try:
            balance = self.exchanges[exchange_name].fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Failed to fetch balance from {exchange_name}: {e}")
            return None
