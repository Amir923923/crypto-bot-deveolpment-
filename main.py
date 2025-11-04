#!/usr/bin/env python3
"""
Main entry point for the crypto trading bot.
"""

import argparse
import sys
from pathlib import Path

from src.bot import CryptoBot
from src.utils.logger import get_logger


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Cryptocurrency Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default config
  python main.py --interval 300     # Run with 5-minute intervals
  python main.py --config custom.yaml  # Use custom config file
  python main.py --once             # Run once and exit
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='Time interval between trading iterations in seconds (default: 3600 = 1 hour)'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run only one iteration and exit'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not Path(args.config).exists():
        print(f"Error: Configuration file '{args.config}' not found")
        print("Please create a config.yaml file or specify a valid config file with --config")
        sys.exit(1)
    
    try:
        # Initialize bot
        bot = CryptoBot(config_path=args.config)
        
        if args.once:
            # Run once and exit
            bot.run_iteration()
        else:
            # Run continuously
            bot.start(interval=args.interval)
    
    except KeyboardInterrupt:
        print("\nBot interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
