"""Example entrypoint for basic-kvm."""
from __future__ import annotations

import argparse


def greet(name: str | None = None) -> str:
    if name:
        return f"Hello, {name}! Welcome to basic-kvm."
    return "Hello! Welcome to basic-kvm."


def main() -> int:
    parser = argparse.ArgumentParser(description="basic-kvm example CLI")
    parser.add_argument("--name", help="Your name", default=None)
    args = parser.parse_args()
    print(greet(args.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
