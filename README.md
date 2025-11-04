# 🤖 Professional Crypto Trading Bot

A sophisticated cryptocurrency trading bot with multiple technical analysis strategies, comprehensive risk management, and robust error handling.

## ✨ Features

### 🎯 Trading Strategies
- **Moving Average Crossover**: Detects trend changes using fast and slow moving averages
- **RSI (Relative Strength Index)**: Identifies overbought and oversold conditions
- **Bollinger Bands**: Trades based on price volatility and bands
- **Multi-Strategy Signal Aggregation**: Combines signals from multiple strategies for better accuracy

### 🛡️ Risk Management
- Configurable stop-loss and take-profit levels
- Maximum position limits
- Daily loss limits
- Position sizing based on available balance
- Automatic position monitoring

### 🔧 Technical Features
- Support for multiple cryptocurrency exchanges via CCXT
- Paper trading mode for testing strategies
- Real-time market data fetching
- Comprehensive logging system
- Database integration for trade history
- Configurable timeframes and trading pairs
- Error handling and recovery mechanisms

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Amir923923/crypto-bot-deveolpment-.git
cd crypto-bot-deveolpment-

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your exchange API credentials:

```env
EXCHANGE_NAME=binance
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
TRADING_MODE=paper  # Use 'paper' for testing, 'live' for real trading
```

Configure your trading parameters in `config.yaml`:

```yaml
trading:
  mode: paper
  symbols:
    - BTC/USDT
    - ETH/USDT
  trade_amount: 100
  max_positions: 3
  
strategies:
  moving_average:
    enabled: true
    fast_period: 10
    slow_period: 30
```

### 3. Running the Bot

#### Run continuously (default 1-hour intervals):
```bash
python main.py
```

#### Run with custom interval (5 minutes):
```bash
python main.py --interval 300
```

#### Run once and exit (for testing):
```bash
python main.py --once
```

#### Use custom config file:
```bash
python main.py --config my_config.yaml
```

## 📊 Trading Strategies Explained

### Moving Average Strategy
Generates signals when fast MA crosses above (buy) or below (sell) the slow MA.

**Configuration:**
```yaml
moving_average:
  enabled: true
  fast_period: 10   # Fast moving average period
  slow_period: 30   # Slow moving average period
```

### RSI Strategy
Identifies oversold (potential buy) and overbought (potential sell) conditions.

**Configuration:**
```yaml
rsi:
  enabled: true
  period: 14        # RSI calculation period
  oversold: 30      # Buy signal threshold
  overbought: 70    # Sell signal threshold
```

### Bollinger Bands Strategy
Trades when price touches upper (sell) or lower (buy) bands.

**Configuration:**
```yaml
bollinger_bands:
  enabled: true
  period: 20        # Moving average period
  std_dev: 2        # Standard deviations for bands
```

## 🛡️ Risk Management

The bot includes comprehensive risk management:

- **Stop Loss**: Automatically closes positions at a configurable loss percentage
- **Take Profit**: Automatically closes positions at a configurable profit percentage
- **Position Limits**: Limits the number of concurrent open positions
- **Daily Loss Limit**: Stops trading if daily loss exceeds the configured threshold
- **Position Sizing**: Calculates appropriate position sizes based on available balance

**Configuration:**
```yaml
trading:
  stop_loss_percentage: 2.0      # Stop loss at 2% below entry
  take_profit_percentage: 5.0    # Take profit at 5% above entry
  max_positions: 3                # Max 3 concurrent positions
  max_daily_loss: 10.0           # Stop if daily loss > 10%
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_strategies.py

# Run with verbose output
pytest -v
```

## 📁 Project Structure

```
crypto-bot-deveolpment-/
├── src/
│   ├── bot.py                  # Main bot orchestrator
│   ├── config.py               # Configuration management
│   ├── exchange/
│   │   └── exchange_interface.py  # Exchange connectivity
│   ├── strategies/
│   │   ├── base_strategy.py    # Base strategy class
│   │   ├── moving_average_strategy.py
│   │   ├── rsi_strategy.py
│   │   └── bollinger_bands_strategy.py
│   ├── risk/
│   │   └── risk_manager.py     # Risk and position management
│   └── utils/
│       └── logger.py           # Logging configuration
├── tests/
│   ├── test_strategies.py      # Strategy tests
│   └── test_risk_manager.py    # Risk manager tests
├── main.py                     # Entry point
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔒 Security Best Practices

1. **Never commit API keys**: Use `.env` files and keep them out of version control
2. **Start with paper trading**: Test strategies thoroughly before using real money
3. **Use testnet/sandbox**: Enable testnet mode when available
4. **Set reasonable limits**: Configure stop-loss and position limits
5. **Monitor regularly**: Check logs and positions frequently
6. **Keep secrets safe**: Store API credentials securely

## 📈 Usage Examples

### Example 1: Conservative Day Trading
```yaml
trading:
  timeframe: 15m
  trade_amount: 50
  max_positions: 2
  stop_loss_percentage: 1.0
  take_profit_percentage: 2.0
```

### Example 2: Aggressive Swing Trading
```yaml
trading:
  timeframe: 4h
  trade_amount: 200
  max_positions: 5
  stop_loss_percentage: 3.0
  take_profit_percentage: 10.0
```

## 🐛 Troubleshooting

### Bot won't connect to exchange
- Verify API credentials in `.env` file
- Check if API keys have trading permissions
- Ensure testnet mode matches your API keys

### No trading signals generated
- Check if strategies are enabled in `config.yaml`
- Verify sufficient historical data is available
- Review logs for strategy analysis details

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.8+)

## ⚠️ Disclaimer

This trading bot is provided for educational and research purposes only. Cryptocurrency trading carries significant risk, and you should never trade with money you cannot afford to lose.

**Important warnings:**
- Past performance does not guarantee future results
- Always test strategies in paper trading mode first
- The bot may lose money, especially in volatile markets
- No strategy is guaranteed to be profitable
- Users are responsible for their own trading decisions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 📞 Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Happy Trading! 🚀📈**

Remember to always trade responsibly and never invest more than you can afford to lose.
