# Crypto Arbitrage Bot

A sophisticated cryptocurrency arbitrage trading bot that monitors multiple exchanges for price discrepancies and automatically executes profitable trades.

## Features

- **Multi-Exchange Support**: Monitor prices across multiple exchanges simultaneously (Binance, Kraken, Coinbase, etc.)
- **Real-time Arbitrage Detection**: Continuously scan for profitable price differences
- **Automated Trading**: Execute buy/sell orders automatically when opportunities are found
- **Risk Management**: Built-in slippage protection and profit threshold validation
- **Dry Run Mode**: Test strategies without risking real funds
- **Comprehensive Logging**: Detailed logging of all operations and trades
- **Configurable Parameters**: Easy configuration via environment variables

## How It Works

The bot operates in a continuous loop:

1. **Price Monitoring**: Fetches real-time ticker data from all configured exchanges
2. **Opportunity Detection**: Compares prices across exchanges to identify arbitrage opportunities
3. **Profit Calculation**: Calculates net profit after accounting for trading fees
4. **Trade Execution**: Executes buy and sell orders when profit exceeds minimum threshold
5. **Risk Management**: Validates opportunities before execution to prevent losses from price movements

## Architecture

```
bot.py                  - Main application controller
├── config.py          - Configuration management
├── exchange_manager.py - Exchange API integration
├── arbitrage_detector.py - Opportunity detection logic
└── trading_engine.py   - Trade execution engine
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Amir923923/crypto-bot-deveolpment-.git
cd crypto-bot-deveolpment-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## Configuration

Edit the `.env` file to configure the bot:

### Trading Configuration
- `MIN_PROFIT_PERCENTAGE`: Minimum profit percentage to execute trades (default: 0.5%)
- `TRADE_AMOUNT_USD`: Amount to trade per opportunity in USD (default: 100)
- `DRY_RUN`: Set to `true` for simulation mode, `false` for live trading (default: true)

### Monitoring Configuration
- `CHECK_INTERVAL_SECONDS`: Time between scans in seconds (default: 10)
- `TRADING_PAIRS`: Comma-separated list of trading pairs (default: BTC/USDT,ETH/USDT)
- `EXCHANGES`: Comma-separated list of exchanges to monitor (default: binance,kraken)

### Exchange API Keys (Optional - only for live trading)
- `BINANCE_API_KEY` and `BINANCE_SECRET`
- `KRAKEN_API_KEY` and `KRAKEN_SECRET`

**Note**: API keys are only required for live trading. The bot can monitor prices without API keys in dry run mode.

## Usage

### Dry Run Mode (Recommended for testing)

Run the bot in simulation mode to test strategies without risking funds:

```bash
python bot.py
```

The bot will:
- Monitor exchanges for arbitrage opportunities
- Log potential trades without executing them
- Show expected profits and trade details

### Live Trading Mode

**⚠️ Warning**: Only enable live trading after thorough testing in dry run mode.

1. Set `DRY_RUN=false` in `.env`
2. Add your exchange API keys to `.env`
3. Run the bot:

```bash
python bot.py
```

### Single Scan Mode

To perform a single scan and exit:

```python
from bot import ArbitrageBot

bot = ArbitrageBot()
bot.scan_once()
```

## Safety Features

- **Dry Run Mode**: Test without real money
- **Slippage Protection**: Validates prices haven't moved too much before execution
- **Profit Validation**: Re-checks profitability immediately before trading
- **Fee Accounting**: Includes trading fees in profit calculations
- **Rate Limiting**: Built-in rate limiting to comply with exchange APIs

## Example Output

```
2025-11-04 20:00:00 - INFO - Crypto Arbitrage Bot v1.0
2025-11-04 20:00:00 - INFO - Bot Configuration:
2025-11-04 20:00:00 - INFO -   Mode: DRY RUN
2025-11-04 20:00:00 - INFO -   Min Profit: 0.5%
2025-11-04 20:00:00 - INFO -   Trade Amount: $100
2025-11-04 20:00:00 - INFO - Scanning for arbitrage opportunities...
2025-11-04 20:00:01 - INFO - Found opportunity: Buy BTC/USDT on binance @ 43500.00, Sell on kraken @ 43750.00 | Profit: 0.37% ($1.50)
2025-11-04 20:00:01 - INFO - [DRY RUN] Would execute arbitrage:
2025-11-04 20:00:01 - INFO -   1. Buy 0.002299 BTC/USDT on binance @ 43500.0
2025-11-04 20:00:01 - INFO -   2. Sell 0.002299 BTC/USDT on kraken @ 43750.0
2025-11-04 20:00:01 - INFO -   Expected profit: $1.50 (0.37%)
```

## Risk Disclaimer

**⚠️ IMPORTANT**: Cryptocurrency trading carries significant risk. This bot is provided for educational purposes.

- **Test thoroughly** in dry run mode before live trading
- **Start with small amounts** when testing live trading
- **Monitor regularly** when running in live mode
- **Understand the risks** of cryptocurrency trading
- **Be aware of exchange fees** and withdrawal limits
- **Consider market volatility** and liquidity

The authors are not responsible for any financial losses incurred through the use of this software.

## Troubleshooting

### "Exchange not initialized"
- Check that the exchange name is spelled correctly in `.env`
- Verify the exchange is supported by CCXT library

### "Failed to fetch ticker"
- Check your internet connection
- Verify the trading pair is available on the exchange
- Some exchanges require API keys even for public data

### "Price moved too much"
- This is normal - it means the opportunity disappeared before execution
- Consider adjusting `MAX_SLIPPAGE_PERCENTAGE` in config.py

### Rate Limiting Errors
- Increase `CHECK_INTERVAL_SECONDS` to reduce API calls
- Enable rate limiting is set to true (default)

## Development

### Project Structure

```
crypto-bot-deveolpment-/
├── bot.py                  # Main application
├── config.py              # Configuration
├── exchange_manager.py    # Exchange API wrapper
├── arbitrage_detector.py  # Opportunity detection
├── trading_engine.py      # Trade execution
├── requirements.txt       # Python dependencies
├── .env.example          # Example configuration
└── README.md             # This file
```

### Adding New Exchanges

1. Add exchange name to `EXCHANGES` in `.env`
2. If API keys needed, add to `.env` and `config.py`
3. Update exchange initialization in `exchange_manager.py` if custom config needed

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests (when implemented)
pytest tests/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly in dry run mode
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation carefully

## Acknowledgments

- Built with [CCXT](https://github.com/ccxt/ccxt) - Cryptocurrency exchange trading library
- Inspired by the cryptocurrency arbitrage trading community

---

**Remember**: Always test in dry run mode first, start with small amounts, and never risk more than you can afford to lose.
