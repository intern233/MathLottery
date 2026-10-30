"""Private workspace proxy defaults, separate from exportable research configuration."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

PROXY_GROUPS = tuple((key, key.lower()) for key in (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
))
PROXY_KEYS = frozenset(key for group in PROXY_GROUPS for key in group)


class NetworkConfigError(ValueError):
    def __init__(self):
        super().__init__(
            "Invalid local network settings. Check .mathlottery/network.json: use a JSON object "
            "containing only HTTP_PROXY, HTTPS_PROXY, ALL_PROXY and NO_PROXY (or lowercase names) "
            "with string values. Do not put account credentials or other environment variables there."
        )


def network_environment(root: Path, inherited=None) -> dict[str, str]:
    """Return a copy; explicit environment settings win, including empty overrides."""
    environment = dict(os.environ if inherited is None else inherited)
    path = Path(root) / ".mathlottery" / "network.json"
    try:
        if not path.exists() and not path.is_symlink():
            return environment
        info = path.lstat()
        if (path.parent.is_symlink() or not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1 or info.st_size > 16_384):
            raise ValueError
        settings = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(settings, dict) or set(settings) - PROXY_KEYS:
            raise ValueError
        if any(not isinstance(value, str) or len(value) > 8192
               or any(char in value for char in "\r\n\0") for value in settings.values()):
            raise ValueError
        for group in PROXY_GROUPS:
            values = {settings[key] for key in group if key in settings}
            if len(values) > 1:
                raise ValueError
            # A saved lowercase proxy must not override an explicit uppercase proxy.
            if values and not any(key in environment for key in group):
                value = values.pop()
                environment.update({key: value for key in group})
    except (OSError, ValueError, UnicodeError):
        raise NetworkConfigError() from None
    return environment


def apply_network_environment(root: Path) -> None:
    """Apply defaults to this CLI/server/worker process, never to its parent shell."""
    os.environ.update(network_environment(root))
