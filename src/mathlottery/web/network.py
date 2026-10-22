"""Local access policy, including the Windows host of a NAT-mode WSL instance."""

from __future__ import annotations

import ipaddress
import json
import platform
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LocalAccess:
    bind: str = "127.0.0.1"
    browser_host: str = "127.0.0.1"
    hosts: tuple[str, ...] = ("127.0.0.1", "localhost")
    peers: tuple[str, ...] = ("127.0.0.1",)

    def accepts(self, address):
        return address in self.peers

    def url(self, port, host=None):
        suffix = f":{port}" if port != 80 else ""
        return f"http://{host or self.browser_host}{suffix}"

    def identity(self):
        return json.loads(json.dumps(asdict(self)))


def is_wsl():
    return "microsoft" in platform.release().lower()


def windows_excluded_ports():
    """Read Windows TCP reservations without changing networking or firewall settings."""
    if not is_wsl() or not shutil.which("netsh.exe"):
        return ()
    try:
        output = subprocess.check_output(
            ["netsh.exe", "interface", "ipv4", "show", "excludedportrange", "protocol=tcp"],
            timeout=3, stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return ()
    # Numeric rows are stable across Windows display languages; ignore all headers.
    ranges = []
    for match in re.finditer(rb"^\s*(\d+)\s+(\d+)\s*\*?\s*$", output, re.MULTILINE):
        start, end = map(int, match.groups())
        if 0 < start <= end <= 65535:
            ranges.append((start, end))
    return tuple(ranges)


def detect_access(loopback_only=False, wsl_direct=False):
    access = LocalAccess()
    if loopback_only or not wsl_direct or not is_wsl():
        return access
    if not shutil.which("wslinfo") or not shutil.which("ip"):
        return access
    try:
        mode = subprocess.check_output(
            ["wslinfo", "--networking-mode"], text=True, timeout=2, stderr=subprocess.DEVNULL,
        ).strip()
        if mode != "nat":
            return access
        # This is a routing-table query, not a connection to the destination.
        route = json.loads(subprocess.check_output(
            ["ip", "-j", "-4", "route", "get", "1.1.1.1"],
            text=True, timeout=2, stderr=subprocess.DEVNULL,
        ))[0]
        address, gateway = str(ipaddress.IPv4Address(route["prefsrc"])), str(ipaddress.IPv4Address(route["gateway"]))
        if not all(ipaddress.ip_address(ip).is_private for ip in (address, gateway)):
            return access
        return LocalAccess(
            bind="0.0.0.0", browser_host=address,
            hosts=(*access.hosts, address), peers=(*access.peers, address, gateway),
        )
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, IndexError, TypeError):
        return access
