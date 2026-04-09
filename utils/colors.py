"""Minimal ANSI color helper for CLI output."""

from __future__ import annotations


COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
}


def colored(text: str, color: str) -> str:
    if color not in COLORS:
        return text
    return f"{COLORS[color]}{text}{COLORS['reset']}"
