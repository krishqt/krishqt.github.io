"""Multithreaded port scanner implementation."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


SERVICE_MAP = {
    21: "FTP",
    22: "SSH",
    80: "HTTP",
    443: "HTTP",
    8080: "HTTP",
}


@dataclass(frozen=True, slots=True)
class PortScanResult:
    port: int
    service: str
    banner: str


class PortScanner:
    def __init__(self, target: str, timeout: float = 0.7, max_workers: int = 200) -> None:
        self.target = target
        self.timeout = timeout
        self.max_workers = max_workers

    def scan_range(self, start_port: int, end_port: int) -> list[PortScanResult]:
        open_ports: list[PortScanResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._scan_port, port) for port in range(start_port, end_port + 1)]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    open_ports.append(result)

        return sorted(open_ports, key=lambda r: r.port)

    def _scan_port(self, port: int) -> PortScanResult | None:
        try:
            addresses = socket.getaddrinfo(self.target, port, type=socket.SOCK_STREAM)
        except OSError:
            return None

        for family, socktype, proto, _, sockaddr in addresses:
            with socket.socket(family, socktype, proto) as sock:
                sock.settimeout(self.timeout)
                try:
                    if sock.connect_ex(sockaddr) != 0:
                        continue
                    service, banner = self._detect_service(sock, port)
                    return PortScanResult(port=port, service=service, banner=banner)
                except OSError:
                    continue

        return None

    def _detect_service(self, sock: socket.socket, port: int) -> tuple[str, str]:
        service = SERVICE_MAP.get(port, "Unknown")
        banner = ""

        try:
            if service == "HTTP":
                sock.sendall(b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n")
                response = sock.recv(128).decode(errors="ignore").strip()
                banner = response.splitlines()[0] if response else "HTTP service"
            elif service in {"FTP", "SSH"}:
                response = sock.recv(128).decode(errors="ignore").strip()
                banner = response.splitlines()[0] if response else f"{service} service"
            else:
                banner = "Open port"
        except OSError:
            banner = f"{service} service" if service != "Unknown" else "Open port"

        return service, banner
