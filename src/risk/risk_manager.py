"""
Risk management for the trading bot.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger()


class Position:
    """Represents a trading position."""
    
    def __init__(self, symbol: str, side: str, entry_price: float, amount: float, 
                 stop_loss: Optional[float] = None, take_profit: Optional[float] = None):
        """Initialize position."""
        self.symbol = symbol
        self.side = side  # 'long' or 'short'
        self.entry_price = entry_price
        self.amount = amount
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = datetime.now()
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0.0
        self.status = 'open'  # 'open' or 'closed'
    
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate current profit/loss."""
        if self.side == 'long':
            self.pnl = (current_price - self.entry_price) * self.amount
        else:  # short
            self.pnl = (self.entry_price - current_price) * self.amount
        return self.pnl
    
    def should_stop_loss(self, current_price: float) -> bool:
        """Check if stop loss should trigger."""
        if self.stop_loss is None:
            return False
        
        if self.side == 'long':
            return current_price <= self.stop_loss
        else:  # short
            return current_price >= self.stop_loss
    
    def should_take_profit(self, current_price: float) -> bool:
        """Check if take profit should trigger."""
        if self.take_profit is None:
            return False
        
        if self.side == 'long':
            return current_price >= self.take_profit
        else:  # short
            return current_price <= self.take_profit
    
    def close(self, exit_price: float):
        """Close the position."""
        self.exit_price = exit_price
        self.exit_time = datetime.now()
        self.status = 'closed'
        self.calculate_pnl(exit_price)
        logger.info(f"Position closed: {self.symbol} {self.side} PnL={self.pnl:.2f}")


class RiskManager:
    """Manages risk for trading operations."""
    
    def __init__(self, config: Dict):
        """
        Initialize risk manager.
        
        Args:
            config: Risk management configuration
        """
        self.config = config
        self.max_positions = config.get('max_positions', 3)
        self.stop_loss_pct = config.get('stop_loss_percentage', 2.0) / 100
        self.take_profit_pct = config.get('take_profit_percentage', 5.0) / 100
        self.max_daily_loss_pct = config.get('max_daily_loss', 10.0) / 100
        self.trade_amount = config.get('trade_amount', 100)
        
        self.positions: Dict[str, Position] = {}
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def can_open_position(self) -> bool:
        """Check if new position can be opened."""
        open_positions = sum(1 for p in self.positions.values() if p.status == 'open')
        
        if open_positions >= self.max_positions:
            logger.warning(f"Max positions reached ({self.max_positions})")
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -abs(self.trade_amount * self.max_daily_loss_pct * self.max_positions):
            logger.warning(f"Daily loss limit reached (PnL={self.daily_pnl:.2f})")
            return False
        
        return True
    
    def calculate_position_size(self, price: float, balance: float) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            price: Current price
            balance: Available balance
            
        Returns:
            Position size (amount)
        """
        # Use configured trade amount or a percentage of balance
        max_amount = min(self.trade_amount, balance * 0.9)  # Use max 90% of balance
        position_size = max_amount / price
        
        logger.debug(f"Calculated position size: {position_size:.6f} at price {price:.2f}")
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price."""
        if side == 'long':
            return entry_price * (1 - self.stop_loss_pct)
        else:  # short
            return entry_price * (1 + self.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate take profit price."""
        if side == 'long':
            return entry_price * (1 + self.take_profit_pct)
        else:  # short
            return entry_price * (1 - self.take_profit_pct)
    
    def open_position(self, symbol: str, side: str, entry_price: float, amount: float) -> Position:
        """
        Open a new position.
        
        Args:
            symbol: Trading pair symbol
            side: 'long' or 'short'
            entry_price: Entry price
            amount: Position amount
            
        Returns:
            Position object
        """
        stop_loss = self.calculate_stop_loss(entry_price, side)
        take_profit = self.calculate_take_profit(entry_price, side)
        
        position = Position(symbol, side, entry_price, amount, stop_loss, take_profit)
        self.positions[symbol] = position
        
        logger.info(f"Opened {side} position: {symbol} amount={amount:.6f} entry={entry_price:.2f} "
                   f"SL={stop_loss:.2f} TP={take_profit:.2f}")
        
        return position
    
    def close_position(self, symbol: str, exit_price: float):
        """Close a position."""
        if symbol in self.positions:
            position = self.positions[symbol]
            if position.status == 'open':
                position.close(exit_price)
                self.daily_pnl += position.pnl
                logger.info(f"Closed position {symbol}: PnL={position.pnl:.2f}, Daily PnL={self.daily_pnl:.2f}")
    
    def check_positions(self, current_prices: Dict[str, float]):
        """
        Check all open positions for stop loss or take profit.
        
        Args:
            current_prices: Dictionary of symbol -> current price
        """
        for symbol, position in self.positions.items():
            if position.status == 'open' and symbol in current_prices:
                current_price = current_prices[symbol]
                
                if position.should_stop_loss(current_price):
                    logger.warning(f"Stop loss triggered for {symbol} at {current_price:.2f}")
                    self.close_position(symbol, current_price)
                
                elif position.should_take_profit(current_price):
                    logger.info(f"Take profit triggered for {symbol} at {current_price:.2f}")
                    self.close_position(symbol, current_price)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for symbol."""
        return self.positions.get(symbol)
    
    def has_open_position(self, symbol: str) -> bool:
        """Check if there's an open position for symbol."""
        position = self.positions.get(symbol)
        return position is not None and position.status == 'open'
    
    def reset_daily_stats(self):
        """Reset daily statistics if a new day has started."""
        now = datetime.now()
        if now >= self.daily_reset_time + timedelta(days=1):
            logger.info(f"Resetting daily stats. Previous PnL: {self.daily_pnl:.2f}")
            self.daily_pnl = 0.0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_open_positions(self) -> Dict[str, Position]:
        """Get all open positions."""
        return {symbol: pos for symbol, pos in self.positions.items() if pos.status == 'open'}
    
    def get_total_pnl(self) -> float:
        """Get total PnL from all positions."""
        return sum(pos.pnl for pos in self.positions.values())
