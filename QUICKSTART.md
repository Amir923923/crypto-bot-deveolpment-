# 🚀 Quick Start Guide

This guide will help you get started with the Crypto Trading Bot in just a few minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure the Bot

### Option A: Paper Trading (Recommended for Testing)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set:
   ```env
   TRADING_MODE=paper
   EXCHANGE_NAME=binance
   ```

3. No API keys needed for paper trading!

### Option B: Live Trading (Use with Caution)

1. Get API credentials from your exchange (e.g., Binance, Coinbase)

2. Edit `.env` and add your credentials:
   ```env
   TRADING_MODE=live
   EXCHANGE_NAME=binance
   API_KEY=your_api_key
   API_SECRET=your_api_secret
   ```

## Step 3: Customize Trading Settings

Edit `config.yaml` to configure:

- **Trading Pairs**: Which cryptocurrencies to trade
- **Strategies**: Which strategies to enable/disable
- **Risk Management**: Stop loss, take profit, position limits
- **Timeframe**: How often to check for trades

Example configuration:
```yaml
trading:
  mode: paper
  symbols:
    - BTC/USDT
    - ETH/USDT
  trade_amount: 100
  max_positions: 3
  stop_loss_percentage: 2.0
  take_profit_percentage: 5.0

strategies:
  moving_average:
    enabled: true
    fast_period: 10
    slow_period: 30
  
  rsi:
    enabled: true
    period: 14
    oversold: 30
    overbought: 70
```

## Step 4: Run the Bot

### Test with Single Iteration
```bash
python main.py --once
```

This will:
- Initialize the bot
- Fetch market data
- Analyze with strategies
- Log potential trades
- Exit

### Run Continuously
```bash
python main.py
```

This will run the bot continuously, checking for trades every hour (default).

### Custom Interval (e.g., every 5 minutes)
```bash
python main.py --interval 300
```

## Step 5: Monitor the Bot

Watch the logs in real-time:
```bash
tail -f logs/crypto_bot.log
```

The bot will show:
- Market analysis results
- Strategy signals
- Trade executions (paper or live)
- Position updates
- Profit/Loss tracking

## Step 6: Run Tests

Verify everything works:
```bash
pytest tests/ -v
```

## Common Commands

```bash
# Run with default settings
python main.py

# Run once and exit (for testing)
python main.py --once

# Run with custom interval (seconds)
python main.py --interval 300

# Use custom config file
python main.py --config my_config.yaml

# Show help
python main.py --help

# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

## Understanding the Output

When the bot runs, you'll see output like:

```
2025-11-04 20:37:27 | INFO | Initializing Crypto Trading Bot
2025-11-04 20:37:27 | INFO | Connected to binance exchange (testnet=True)
2025-11-04 20:37:27 | INFO | Enabled Moving Average strategy
2025-11-04 20:37:27 | INFO | Trading mode: paper
2025-11-04 20:37:27 | INFO | Symbols: BTC/USDT, ETH/USDT
2025-11-04 20:37:27 | INFO | Analyzing BTC/USDT...
2025-11-04 20:37:27 | INFO | BTC/USDT current price: 45000.00
2025-11-04 20:37:27 | INFO | MA Strategy: Bullish crossover detected
2025-11-04 20:37:27 | INFO | Aggregated signal for BTC/USDT: BUY (2/3)
2025-11-04 20:37:27 | INFO | [PAPER] Would BUY 0.002222 BTC/USDT at 45000.00
2025-11-04 20:37:27 | INFO | Opened long position: BTC/USDT
```

## Next Steps

1. **Backtest**: Test your strategies on historical data
2. **Optimize**: Tune strategy parameters for better performance
3. **Monitor**: Regularly check bot logs and positions
4. **Adjust**: Modify settings based on market conditions

## Safety Tips

⚠️ **Important Reminders:**

1. **Start with paper trading** - Always test first!
2. **Use small amounts** - Start with minimal trade sizes
3. **Set stop losses** - Protect your capital
4. **Monitor regularly** - Check the bot frequently
5. **Never invest more than you can afford to lose**

## Troubleshooting

### Bot won't start
- Check if config.yaml exists
- Verify Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`

### No trading signals
- Ensure strategies are enabled in config.yaml
- Check if sufficient historical data is available
- Review log files for errors

### Exchange connection errors
- Verify API credentials in .env
- Check if API keys have trading permissions
- Ensure correct exchange name is set

## Support

For questions or issues:
1. Check the main README.md
2. Review log files in `logs/`
3. Open an issue on GitHub

---

**Happy Trading! 📈🚀**
