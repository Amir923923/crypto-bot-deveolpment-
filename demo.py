#!/usr/bin/env python3
"""
Demo script to showcase the arbitrage bot functionality with mock data.
This demonstrates how the bot works without requiring live exchange connections.
"""
import logging
from dataclasses import dataclass
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MockTicker:
    """Mock ticker data for demonstration."""
    bid: float
    ask: float
    last: float
    timestamp: float


class ArbitrageDemo:
    """Demonstrate arbitrage detection with mock data."""
    
    def __init__(self):
        """Initialize the demo."""
        logger.info("=" * 70)
        logger.info("Crypto Arbitrage Bot - Demo Mode")
        logger.info("=" * 70)
    
    def create_mock_tickers(self) -> Dict[str, Dict[str, MockTicker]]:
        """
        Create mock ticker data representing different scenarios.
        
        Returns:
            Dictionary of exchange -> symbol -> ticker
        """
        return {
            'binance': {
                'BTC/USDT': MockTicker(bid=43200.00, ask=43250.00, last=43225.00, timestamp=1699128000.0),
                'ETH/USDT': MockTicker(bid=2285.50, ask=2287.00, last=2286.25, timestamp=1699128000.0),
            },
            'kraken': {
                'BTC/USDT': MockTicker(bid=43550.00, ask=43600.00, last=43575.00, timestamp=1699128000.0),
                'ETH/USDT': MockTicker(bid=2300.00, ask=2302.50, last=2301.25, timestamp=1699128000.0),
            },
            'coinbase': {
                'BTC/USDT': MockTicker(bid=43400.00, ask=43450.00, last=43425.00, timestamp=1699128000.0),
                'ETH/USDT': MockTicker(bid=2293.00, ask=2294.50, last=2293.75, timestamp=1699128000.0),
            }
        }
    
    def calculate_arbitrage(self, buy_exchange: str, sell_exchange: str, 
                           symbol: str, tickers: Dict) -> Dict:
        """Calculate arbitrage opportunity."""
        buy_ticker = tickers[buy_exchange][symbol]
        sell_ticker = tickers[sell_exchange][symbol]
        
        buy_price = buy_ticker.ask  # Price we pay to buy
        sell_price = sell_ticker.bid  # Price we receive when selling
        
        # Calculate profit
        gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100
        fees_pct = 0.2  # Assume 0.1% per trade
        net_profit_pct = gross_profit_pct - fees_pct
        
        # Calculate profit in USD for $100 trade
        trade_amount = 100.0
        quantity = trade_amount / buy_price
        revenue = quantity * sell_price
        fees = (trade_amount + revenue) * 0.001
        profit_usd = revenue - trade_amount - fees
        
        return {
            'buy_exchange': buy_exchange,
            'sell_exchange': sell_exchange,
            'symbol': symbol,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'profit_pct': net_profit_pct,
            'profit_usd': profit_usd,
            'quantity': quantity
        }
    
    def find_opportunities(self, tickers: Dict, symbol: str) -> list:
        """Find all arbitrage opportunities for a symbol."""
        opportunities = []
        exchanges = list(tickers.keys())
        
        for i, buy_ex in enumerate(exchanges):
            for sell_ex in exchanges[i+1:]:
                # Check both directions
                opp1 = self.calculate_arbitrage(buy_ex, sell_ex, symbol, tickers)
                if opp1['profit_pct'] > 0.3:  # Lower threshold for demo
                    opportunities.append(opp1)
                
                opp2 = self.calculate_arbitrage(sell_ex, buy_ex, symbol, tickers)
                if opp2['profit_pct'] > 0.3:  # Lower threshold for demo
                    opportunities.append(opp2)
        
        return opportunities
    
    def display_opportunity(self, opp: Dict):
        """Display an arbitrage opportunity."""
        logger.info("")
        logger.info("  " + "=" * 66)
        logger.info(f"  Arbitrage Opportunity Found!")
        logger.info("  " + "=" * 66)
        logger.info(f"  Symbol: {opp['symbol']}")
        logger.info(f"  Buy from: {opp['buy_exchange']} @ ${opp['buy_price']:,.2f}")
        logger.info(f"  Sell on:  {opp['sell_exchange']} @ ${opp['sell_price']:,.2f}")
        logger.info(f"  Quantity: {opp['quantity']:.8f}")
        logger.info(f"  Profit:   ${opp['profit_usd']:.2f} ({opp['profit_pct']:.2f}%)")
        logger.info("  " + "=" * 66)
    
    def run(self):
        """Run the demo."""
        logger.info("\n📊 Creating mock exchange data...")
        tickers = self.create_mock_tickers()
        
        # Display exchange prices
        logger.info("\n💹 Current Prices Across Exchanges:")
        logger.info("-" * 70)
        for symbol in ['BTC/USDT', 'ETH/USDT']:
            logger.info(f"\n{symbol}:")
            for exchange, data in tickers.items():
                ticker = data[symbol]
                logger.info(f"  {exchange:12s}: Bid: ${ticker.bid:>10,.2f}  Ask: ${ticker.ask:>10,.2f}")
        
        # Find opportunities
        logger.info("\n\n🔍 Scanning for Arbitrage Opportunities...")
        logger.info("-" * 70)
        
        all_opportunities = []
        for symbol in ['BTC/USDT', 'ETH/USDT']:
            opportunities = self.find_opportunities(tickers, symbol)
            all_opportunities.extend(opportunities)
        
        if not all_opportunities:
            logger.info("No profitable opportunities found (min profit: 0.3%)")
        else:
            logger.info(f"Found {len(all_opportunities)} profitable opportunity(ies)!")
            
            # Sort by profit
            all_opportunities.sort(key=lambda x: x['profit_pct'], reverse=True)
            
            # Display all opportunities
            for i, opp in enumerate(all_opportunities, 1):
                self.display_opportunity(opp)
            
            # Show best opportunity
            best = all_opportunities[0]
            logger.info("\n\n✅ Best Opportunity Summary:")
            logger.info("=" * 70)
            logger.info(f"Trade: Buy {best['quantity']:.8f} {best['symbol']} on {best['buy_exchange']}")
            logger.info(f"       Sell on {best['sell_exchange']}")
            logger.info(f"Expected Profit: ${best['profit_usd']:.2f} ({best['profit_pct']:.2f}%)")
            logger.info("=" * 70)
        
        # Show how the bot would execute
        logger.info("\n\n🤖 Bot Execution Flow:")
        logger.info("=" * 70)
        logger.info("1. Monitor prices across exchanges (Binance, Kraken, Coinbase)")
        logger.info("2. Detect price differences and calculate profit")
        logger.info("3. Validate opportunity is still profitable")
        logger.info("4. Execute buy order on cheaper exchange")
        logger.info("5. Execute sell order on expensive exchange")
        logger.info("6. Calculate and log realized profit")
        logger.info("=" * 70)
        
        logger.info("\n\n💡 Configuration Options:")
        logger.info("=" * 70)
        logger.info("• MIN_PROFIT_PERCENTAGE: Minimum profit to execute (default: 0.5%)")
        logger.info("• TRADE_AMOUNT_USD: Amount per trade (default: $100)")
        logger.info("• DRY_RUN: Test without real trades (default: true)")
        logger.info("• CHECK_INTERVAL_SECONDS: Time between scans (default: 10s)")
        logger.info("• TRADING_PAIRS: Pairs to monitor (e.g., BTC/USDT,ETH/USDT)")
        logger.info("• EXCHANGES: Exchanges to use (e.g., binance,kraken,coinbase)")
        logger.info("=" * 70)
        
        logger.info("\n\n🚀 To run the actual bot:")
        logger.info("=" * 70)
        logger.info("1. Configure .env file with your settings")
        logger.info("2. Run: python bot.py")
        logger.info("3. Bot will continuously scan for opportunities")
        logger.info("4. In DRY_RUN mode, it logs trades without executing")
        logger.info("5. In live mode (with API keys), it executes real trades")
        logger.info("=" * 70)
        logger.info("\n")


def main():
    """Main entry point."""
    demo = ArbitrageDemo()
    demo.run()


if __name__ == "__main__":
    main()
