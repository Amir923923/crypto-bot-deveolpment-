"""
Exchange interface for connecting to cryptocurrency exchanges.
"""

import ccxt
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger()


class ExchangeInterface:
    """Interface for interacting with cryptocurrency exchanges."""
    
    def __init__(self, exchange_name: str, api_key: str = "", api_secret: str = "", testnet: bool = True):
        """
        Initialize exchange connection.
        
        Args:
            exchange_name: Name of the exchange (e.g., 'binance', 'coinbase')
            api_key: API key for authentication
            api_secret: API secret for authentication
            testnet: Use testnet/sandbox mode
        """
        self.exchange_name = exchange_name.lower()
        self.testnet = testnet
        
        try:
            # Get exchange class
            exchange_class = getattr(ccxt, self.exchange_name)
            
            # Configure exchange
            config = {
                'enableRateLimit': True,
                'timeout': 30000,
            }
            
            # Add credentials if provided
            if api_key and api_secret:
                config['apiKey'] = api_key
                config['secret'] = api_secret
            
            # Enable testnet if specified
            if testnet and hasattr(exchange_class, 'has') and exchange_class.has.get('sandbox'):
                config['sandbox'] = True
            
            self.exchange = exchange_class(config)
            logger.info(f"Connected to {exchange_name} exchange (testnet={testnet})")
            
        except AttributeError:
            raise ValueError(f"Exchange '{exchange_name}' is not supported")
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise
    
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current ticker data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Dictionary containing ticker data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.debug(f"Fetched ticker for {symbol}: {ticker['last']}")
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[List]:
        """
        Fetch OHLCV (candlestick) data.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV data [timestamp, open, high, low, close, volume]
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            logger.debug(f"Fetched {len(ohlcv)} candles for {symbol} ({timeframe})")
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise
    
    def fetch_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance.
        
        Returns:
            Dictionary containing balance information
        """
        try:
            balance = self.exchange.fetch_balance()
            logger.debug(f"Fetched account balance")
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise
    
    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """
        Create a market order.
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            amount: Amount to trade
            
        Returns:
            Order details
        """
        try:
            order = self.exchange.create_market_order(symbol, side, amount)
            logger.info(f"Created market {side} order for {amount} {symbol}: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error creating market order: {e}")
            raise
    
    def create_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Dict[str, Any]:
        """
        Create a limit order.
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Limit price
            
        Returns:
            Order details
        """
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            logger.info(f"Created limit {side} order for {amount} {symbol} at {price}: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error creating limit order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol
            
        Returns:
            Cancellation details
        """
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Cancelled order {order_id} for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch open orders.
        
        Args:
            symbol: Trading pair symbol (optional, fetches all if not specified)
            
        Returns:
            List of open orders
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.debug(f"Fetched {len(orders)} open orders")
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise
    
    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Fetch order details.
        
        Args:
            order_id: Order ID
            symbol: Trading pair symbol
            
        Returns:
            Order details
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    def get_markets(self) -> Dict[str, Any]:
        """
        Get available markets/trading pairs.
        
        Returns:
            Dictionary of available markets
        """
        try:
            markets = self.exchange.load_markets()
            logger.debug(f"Loaded {len(markets)} markets")
            return markets
        except Exception as e:
            logger.error(f"Error loading markets: {e}")
            raise
