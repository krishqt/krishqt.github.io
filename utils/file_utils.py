"""File helpers for Smart Port Scanner."""

from __future__ import annotations

from datetime import datetime, timezone

from scanner.port_scanner import PortScanResult


def save_scan_results(
    target: str,
    start_port: int,
    end_port: int,
    results: list[PortScanResult],
    output_path: str,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [
        "Smart Port Scanner Report",
        f"Timestamp (UTC): {timestamp}",
        f"Target: {target}",
        f"Port Range: {start_port}-{end_port}",
        f"Open Ports Found: {len(results)}",
        "",
    ]

    if results:
        lines.append("PORT\tSERVICE\tBANNER")
        for item in results:
            lines.append(f"{item.port}\t{item.service}\t{item.banner}")
    else:
        lines.append("No open ports found.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
