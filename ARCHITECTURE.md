# Architecture Documentation

This document explains the architecture and design decisions of the Crypto Trading Bot.

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Extension Guide](#extension-guide)

## Overview

The Crypto Trading Bot is designed with modularity, maintainability, and extensibility in mind. It follows clean architecture principles with clear separation of concerns.

### Key Design Principles
- **Modularity**: Each component has a single responsibility
- **Extensibility**: Easy to add new strategies or exchanges
- **Testability**: Components are independently testable
- **Configuration-Driven**: Behavior controlled via configuration files
- **Error Resilience**: Comprehensive error handling throughout

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Main Bot                            │
│                      (src/bot.py)                           │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐      ┌─────────────────────────┐
│   Exchange Interface   │      │    Risk Manager         │
│  (exchange_interface)  │      │   (risk_manager.py)     │
│                        │      │                         │
│  - Fetch Market Data   │      │  - Position Management  │
│  - Execute Trades      │      │  - Stop Loss/Take Profit│
│  - Get Balance         │      │  - Position Sizing      │
└────────────────────────┘      └─────────────────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐      ┌─────────────────────────┐
│    Trading Strategies  │      │   Configuration         │
│                        │      │   (config.py)           │
│  - Moving Average      │      │                         │
│  - RSI                 │      │  - YAML Config Loader   │
│  - Bollinger Bands     │      │  - Environment Vars     │
└────────────────────────┘      └─────────────────────────┘
             │
             ▼
┌────────────────────────┐
│    Utilities           │
│                        │
│  - Logger              │
│  - Helpers             │
└────────────────────────┘
```

## Core Components

### 1. Bot Core (`src/bot.py`)

The main orchestrator that coordinates all components.

**Responsibilities:**
- Initialize all subsystems
- Run the main trading loop
- Coordinate strategy analysis
- Execute trades through risk manager
- Handle iteration timing

**Key Methods:**
- `__init__()`: Initialize bot with configuration
- `run_iteration()`: Execute one trading cycle
- `analyze_symbol()`: Aggregate strategy signals
- `execute_trade()`: Execute trades with risk checks

### 2. Exchange Interface (`src/exchange/exchange_interface.py`)

Abstracts exchange interactions using CCXT library.

**Responsibilities:**
- Connect to cryptocurrency exchanges
- Fetch market data (OHLCV, tickers)
- Execute orders (market, limit)
- Manage account balance
- Handle API rate limits

**Key Methods:**
- `fetch_ohlcv()`: Get historical price data
- `fetch_ticker()`: Get current price
- `create_market_order()`: Execute market orders
- `fetch_balance()`: Get account balance

**Supported Exchanges:**
Any exchange supported by CCXT (100+), including:
- Binance
- Coinbase
- Kraken
- Bitfinex
- And many more...

### 3. Trading Strategies (`src/strategies/`)

Pluggable strategy modules for market analysis.

#### Base Strategy (`base_strategy.py`)
Abstract base class defining the strategy interface.

**Key Methods:**
- `analyze()`: Generate trading signal (BUY/SELL/HOLD)
- `get_indicators()`: Calculate technical indicators
- `should_execute()`: Check if strategy is enabled

#### Moving Average Strategy (`moving_average_strategy.py`)
Trend-following strategy using moving average crossovers.

**Indicators:**
- Fast Moving Average (default: 10 periods)
- Slow Moving Average (default: 30 periods)

**Signals:**
- BUY: Fast MA crosses above Slow MA
- SELL: Fast MA crosses below Slow MA

#### RSI Strategy (`rsi_strategy.py`)
Momentum strategy using Relative Strength Index.

**Indicators:**
- RSI (default: 14 periods)

**Signals:**
- BUY: RSI < oversold threshold (30)
- SELL: RSI > overbought threshold (70)

#### Bollinger Bands Strategy (`bollinger_bands_strategy.py`)
Volatility-based mean reversion strategy.

**Indicators:**
- Middle Band (SMA)
- Upper Band (SMA + 2 * std dev)
- Lower Band (SMA - 2 * std dev)

**Signals:**
- BUY: Price touches lower band
- SELL: Price touches upper band

### 4. Risk Manager (`src/risk/risk_manager.py`)

Manages positions and enforces risk limits.

**Responsibilities:**
- Position tracking (open/close)
- Stop-loss and take-profit monitoring
- Position sizing calculations
- Daily loss limit enforcement
- Maximum position limit enforcement

**Key Classes:**

#### Position
Represents a single trading position.

**Attributes:**
- symbol, side, entry_price, amount
- stop_loss, take_profit
- pnl, status

#### RiskManager
Manages all positions and risk rules.

**Key Methods:**
- `can_open_position()`: Check if new position allowed
- `open_position()`: Create new position with SL/TP
- `close_position()`: Close existing position
- `check_positions()`: Monitor for SL/TP triggers
- `calculate_position_size()`: Determine trade size

### 5. Configuration (`src/config.py`)

Centralized configuration management.

**Features:**
- YAML file parsing
- Environment variable integration
- Nested configuration access
- Mode detection (paper/live trading)

**Configuration Sources:**
1. `config.yaml`: Main configuration file
2. `.env`: Sensitive credentials and overrides

### 6. Utilities (`src/utils/`)

Helper modules for common operations.

#### Logger (`logger.py`)
Structured logging with rotation and formatting.

**Features:**
- Console and file output
- Colored console logs
- Automatic log rotation
- Configurable log levels

#### Helpers (`helpers.py`)
Common utility functions.

**Functions:**
- Price formatting
- Percentage calculations
- Symbol validation
- Timeframe parsing
- Data frame conversion

## Data Flow

### Trading Iteration Flow

```
1. Start Iteration
   ↓
2. Reset Daily Stats (if needed)
   ↓
3. For Each Symbol:
   ├─→ Fetch Market Data
   │   ↓
   ├─→ Analyze with Strategies
   │   ├─→ Moving Average
   │   ├─→ RSI
   │   └─→ Bollinger Bands
   │   ↓
   ├─→ Aggregate Signals
   │   ↓
   └─→ Execute Trade (if signal != HOLD)
       ├─→ Check Risk Limits
       ├─→ Calculate Position Size
       └─→ Open/Close Position
   ↓
4. Monitor Existing Positions
   ├─→ Check Stop Loss
   └─→ Check Take Profit
   ↓
5. Log Status & Statistics
   ↓
6. Wait for Next Iteration
```

### Signal Aggregation

Multiple strategies vote on each symbol:

```
Strategy 1: BUY  ─┐
Strategy 2: HOLD ─┼─→ Aggregation Logic ─→ Final Signal
Strategy 3: BUY  ─┘

Rules:
- If ≥2 strategies say BUY → BUY
- If ≥2 strategies say SELL → SELL
- Otherwise → HOLD
```

## Design Patterns

### 1. Strategy Pattern
Used for trading strategies - allows easy addition of new strategies.

```python
class BaseStrategy(ABC):
    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> str:
        pass

class NewStrategy(BaseStrategy):
    def analyze(self, df: pd.DataFrame) -> str:
        # Implementation
        return Signal.BUY
```

### 2. Singleton Pattern
Configuration is a singleton to ensure consistent state.

```python
config = get_config()  # Always returns same instance
```

### 3. Factory Pattern
Exchange creation abstracts CCXT library details.

```python
exchange = ExchangeInterface('binance', ...)
# Works with any CCXT-supported exchange
```

### 4. Observer Pattern
Risk manager monitors positions and triggers actions.

```python
risk_manager.check_positions(current_prices)
# Automatically closes positions if SL/TP hit
```

## Extension Guide

### Adding a New Strategy

1. Create a new file in `src/strategies/`:

```python
from src.strategies.base_strategy import BaseStrategy, Signal
import pandas as pd

class MyStrategy(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("My Strategy", config)
        self.param1 = config.get('param1', default_value)
    
    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # Calculate your indicators
        df['my_indicator'] = ...
        return df
    
    def analyze(self, df: pd.DataFrame) -> str:
        # Generate trading signal
        df = self.get_indicators(df)
        if condition_for_buy:
            return Signal.BUY
        elif condition_for_sell:
            return Signal.SELL
        return Signal.HOLD
```

2. Add configuration to `config.yaml`:

```yaml
strategies:
  my_strategy:
    enabled: true
    param1: value1
```

3. Register in `src/bot.py`:

```python
from src.strategies.my_strategy import MyStrategy

def _initialize_strategies(self):
    # ... existing strategies ...
    
    my_config = strategies_config.get('my_strategy', {})
    if my_config.get('enabled', False):
        self.strategies.append(MyStrategy(my_config))
```

### Adding Exchange-Specific Features

The exchange interface can be extended for specific exchange features:

```python
class BinanceExtensions(ExchangeInterface):
    def fetch_funding_rate(self, symbol: str):
        # Binance-specific method
        return self.exchange.fetch_funding_rate(symbol)
```

### Adding New Risk Rules

Extend the `RiskManager` class:

```python
class AdvancedRiskManager(RiskManager):
    def check_volatility_limit(self, symbol: str, volatility: float):
        # Custom risk check
        if volatility > self.max_volatility:
            return False
        return True
```

### Adding Database Storage

Create a database module:

```python
from sqlalchemy import create_engine
from src.config import get_config

class TradeDatabase:
    def __init__(self):
        config = get_config()
        self.engine = create_engine(config.get('database.url'))
    
    def save_trade(self, trade_data):
        # Save to database
        pass
```

## Testing

### Unit Tests
Each component has dedicated unit tests:
- `tests/test_strategies.py`: Strategy tests
- `tests/test_risk_manager.py`: Risk management tests

### Integration Tests
Test component interactions:
- Bot initialization
- End-to-end trading flow
- Error handling

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_strategies.py

# With coverage
pytest --cov=src tests/
```

## Performance Considerations

### Optimization Strategies
1. **Rate Limiting**: Exchange interface respects API limits
2. **Caching**: Could cache indicator calculations
3. **Async Operations**: Potential for async exchange calls
4. **Database**: Use for historical analysis

### Scalability
- Can run multiple bot instances for different symbol sets
- Strategies execute independently
- Modular design allows easy parallelization

## Security Best Practices

1. **API Keys**: Never commit to repository
2. **Environment Variables**: Use for sensitive data
3. **Paper Trading**: Test thoroughly before live trading
4. **Logging**: Avoid logging sensitive information
5. **Error Handling**: Fail safely, don't expose internals

## Future Enhancements

Potential improvements:
1. **Web Dashboard**: Real-time monitoring UI
2. **Backtesting**: Historical strategy testing
3. **Machine Learning**: ML-based strategies
4. **Advanced Orders**: OCO, trailing stops
5. **Portfolio Optimization**: Multi-asset allocation
6. **Alerts**: Telegram/Email notifications
7. **Database Integration**: Trade history storage
8. **Multi-timeframe**: Analyze multiple timeframes
9. **Paper Trading Simulator**: More realistic simulation
10. **API Server**: REST API for remote control

## Contributing

When contributing:
1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Follow Python style guidelines (PEP 8)
5. Test thoroughly before submitting

## Resources

- **CCXT Documentation**: https://docs.ccxt.com
- **TA-Lib**: Technical Analysis Library
- **Pandas**: Data manipulation
- **Python Documentation**: https://docs.python.org

---

For questions about architecture or design decisions, please open an issue on GitHub.
