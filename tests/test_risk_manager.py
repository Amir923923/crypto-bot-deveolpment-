"""
Tests for risk manager.
"""

import pytest
from src.risk.risk_manager import RiskManager, Position


@pytest.fixture
def risk_manager():
    """Create a risk manager instance for testing."""
    config = {
        'max_positions': 3,
        'stop_loss_percentage': 2.0,
        'take_profit_percentage': 5.0,
        'max_daily_loss': 10.0,
        'trade_amount': 100,
    }
    return RiskManager(config)


class TestPosition:
    """Test Position class."""
    
    def test_position_creation(self):
        """Test position creation."""
        position = Position('BTC/USDT', 'long', 50000, 0.002)
        
        assert position.symbol == 'BTC/USDT'
        assert position.side == 'long'
        assert position.entry_price == 50000
        assert position.amount == 0.002
        assert position.status == 'open'
    
    def test_long_pnl_calculation(self):
        """Test PnL calculation for long position."""
        position = Position('BTC/USDT', 'long', 50000, 0.002)
        
        # Price goes up
        pnl = position.calculate_pnl(51000)
        assert pnl == 2.0  # (51000 - 50000) * 0.002
        
        # Price goes down
        pnl = position.calculate_pnl(49000)
        assert pnl == -2.0  # (49000 - 50000) * 0.002
    
    def test_stop_loss_trigger(self):
        """Test stop loss trigger."""
        position = Position('BTC/USDT', 'long', 50000, 0.002, stop_loss=49000)
        
        assert position.should_stop_loss(48000) is True
        assert position.should_stop_loss(49500) is False
        assert position.should_stop_loss(51000) is False
    
    def test_take_profit_trigger(self):
        """Test take profit trigger."""
        position = Position('BTC/USDT', 'long', 50000, 0.002, take_profit=52000)
        
        assert position.should_take_profit(53000) is True
        assert position.should_take_profit(51000) is False
        assert position.should_take_profit(49000) is False
    
    def test_position_close(self):
        """Test position closure."""
        position = Position('BTC/USDT', 'long', 50000, 0.002)
        position.close(51000)
        
        assert position.status == 'closed'
        assert position.exit_price == 51000
        assert position.pnl == 2.0


class TestRiskManager:
    """Test RiskManager class."""
    
    def test_initialization(self, risk_manager):
        """Test risk manager initialization."""
        assert risk_manager.max_positions == 3
        assert risk_manager.stop_loss_pct == 0.02
        assert risk_manager.take_profit_pct == 0.05
        assert risk_manager.trade_amount == 100
    
    def test_can_open_position(self, risk_manager):
        """Test position opening permission."""
        # Should be able to open position initially
        assert risk_manager.can_open_position() is True
        
        # Open max positions
        risk_manager.open_position('BTC/USDT', 'long', 50000, 0.002)
        risk_manager.open_position('ETH/USDT', 'long', 3000, 0.033)
        risk_manager.open_position('BNB/USDT', 'long', 400, 0.25)
        
        # Should not be able to open more
        assert risk_manager.can_open_position() is False
    
    def test_position_size_calculation(self, risk_manager):
        """Test position size calculation."""
        price = 50000
        balance = 1000
        
        size = risk_manager.calculate_position_size(price, balance)
        
        assert size > 0
        assert size * price <= balance * 0.9  # Should use max 90% of balance
    
    def test_stop_loss_calculation(self, risk_manager):
        """Test stop loss calculation."""
        entry_price = 50000
        
        # Long position
        sl = risk_manager.calculate_stop_loss(entry_price, 'long')
        assert sl < entry_price
        assert sl == entry_price * 0.98  # 2% below
        
        # Short position
        sl = risk_manager.calculate_stop_loss(entry_price, 'short')
        assert sl > entry_price
        assert sl == entry_price * 1.02  # 2% above
    
    def test_take_profit_calculation(self, risk_manager):
        """Test take profit calculation."""
        entry_price = 50000
        
        # Long position
        tp = risk_manager.calculate_take_profit(entry_price, 'long')
        assert tp > entry_price
        assert tp == entry_price * 1.05  # 5% above
        
        # Short position
        tp = risk_manager.calculate_take_profit(entry_price, 'short')
        assert tp < entry_price
        assert tp == entry_price * 0.95  # 5% below
    
    def test_open_and_close_position(self, risk_manager):
        """Test opening and closing positions."""
        # Open position
        position = risk_manager.open_position('BTC/USDT', 'long', 50000, 0.002)
        
        assert position is not None
        assert risk_manager.has_open_position('BTC/USDT') is True
        
        # Close position
        risk_manager.close_position('BTC/USDT', 51000)
        
        position = risk_manager.get_position('BTC/USDT')
        assert position.status == 'closed'
    
    def test_check_positions(self, risk_manager):
        """Test position monitoring."""
        # Open position with stop loss and take profit
        risk_manager.open_position('BTC/USDT', 'long', 50000, 0.002)
        
        # Price triggers stop loss
        current_prices = {'BTC/USDT': 48000}
        risk_manager.check_positions(current_prices)
        
        position = risk_manager.get_position('BTC/USDT')
        assert position.status == 'closed'
    
    def test_get_open_positions(self, risk_manager):
        """Test getting open positions."""
        risk_manager.open_position('BTC/USDT', 'long', 50000, 0.002)
        risk_manager.open_position('ETH/USDT', 'long', 3000, 0.033)
        risk_manager.close_position('BTC/USDT', 51000)
        
        open_positions = risk_manager.get_open_positions()
        
        assert len(open_positions) == 1
        assert 'ETH/USDT' in open_positions
        assert 'BTC/USDT' not in open_positions
