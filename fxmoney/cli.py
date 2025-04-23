# fxmoney/cli.py

"""
CLI for fxmoney: provides the `convert` command.
"""

import argparse
from datetime import datetime

from .core import Money
from .rates import install_backend, get_backend
from .rates.ecb import ECBBackend


def main():
    parser = argparse.ArgumentParser(
        prog="fxmoney",
        description="Convert money amounts between currencies using fxmoney."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # convert subcommand
    conv = sub.add_parser(
        "convert", help="Convert an amount from one currency to another"
    )
    conv.add_argument("amount", type=str, help="Amount to convert (e.g. 100.5)")
    conv.add_argument("src",    type=str, help="Source currency code (e.g. USD)")
    conv.add_argument("tgt",    type=str, help="Target currency code (e.g. EUR)")
    conv.add_argument(
        "--date",
        type=str,
        default=None,
        help="Historical date YYYY-MM-DD (default: latest rate)"
    )
    conv.add_argument(
        "--fallback",
        choices=["last", "raise"],
        default=None,
        help="Override fallback mode ('last' or 'raise')"
    )
    conv.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show exchange rate and then the result"
    )

    args = parser.parse_args()

    if args.command == "convert":
        # ensure ECB backend is active by default
        install_backend(ECBBackend())

        # parse optional date
        on_date = (
            datetime.strptime(args.date, "%Y-%m-%d").date()
            if args.date
            else None
        )

        m = Money(args.amount, args.src)
        result = m.to(args.tgt, on_date, args.fallback)

        if args.verbose:
            # fetch the raw rate for 1 unit
            backend = get_backend()
            rate = backend.get_rate(args.src.upper(), args.tgt.upper(), on_date)
            print(f"Rate ({args.src.upper()}→{args.tgt.upper()}): {rate}")
            print(f"Result: {result}")
        else:
            print(result)
