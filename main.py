#!/usr/bin/env python3
"""Smart Port Scanner CLI entry point."""

from __future__ import annotations

import argparse
import ipaddress
import sys

from scanner.port_scanner import PortScanner
from utils.colors import colored
from utils.file_utils import save_scan_results


def parse_port_range(port_range: str) -> tuple[int, int]:
    parts = port_range.split("-", maxsplit=1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Port range must be in format START-END (example: 1-1000).")

    try:
        start, end = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Port range must contain numeric values.") from exc

    if start < 1:
        raise argparse.ArgumentTypeError("Invalid port range: START must be at least 1.")
    if end > 1000:
        raise argparse.ArgumentTypeError("Invalid port range: END must be at most 1000.")
    if start > end:
        raise argparse.ArgumentTypeError("Invalid port range: START must be less than or equal to END.")

    return start, end


def valid_ip(value: str) -> str:
    try:
        ipaddress.ip_address(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Target must be a valid IPv4 or IPv6 address.") from exc
    return value


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Thread count must be an integer.") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("Thread count must be greater than 0.")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smart-port-scanner",
        description="Smart Port Scanner - multithreaded scanner for ports 1-1000.",
    )
    parser.add_argument("-t", "--target", required=True, type=valid_ip, help="Target IP address.")
    parser.add_argument(
        "-p",
        "--ports",
        default="1-1000",
        type=parse_port_range,
        help="Port range in START-END format (default: 1-1000).",
    )
    parser.add_argument(
        "-T",
        "--threads",
        type=positive_int,
        default=200,
        help="Number of worker threads to use (default: 200).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.7,
        help="Connection timeout in seconds (default: 0.7).",
    )
    parser.add_argument("-o", "--output", default="scan_results.txt", help="Output file path.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    port_start, port_end = args.ports
    scanner = PortScanner(target=args.target, timeout=args.timeout, max_workers=args.threads)

    print(colored(f"\n[*] Scanning {args.target} ports {port_start}-{port_end}...", "blue"))
    results = scanner.scan_range(port_start, port_end)
    print(colored(f"[*] Scan complete. Open ports found: {len(results)}\n", "green"))

    if results:
        for result in results:
            print(
                colored(
                    f"[+] Port {result.port:<5} OPEN  Service: {result.service:<10} Banner: {result.banner or '-'}",
                    "green",
                )
            )
    else:
        print(colored("[-] No open ports found in selected range.", "yellow"))

    save_scan_results(args.target, port_start, port_end, results, args.output)
    print(colored(f"\n[*] Results saved to: {args.output}", "cyan"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
