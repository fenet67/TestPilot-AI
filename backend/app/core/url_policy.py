"""Target-URL policy.

The agent drives a real browser at a URL supplied by the user. That makes the URL
untrusted input, and an unchecked one is a server-side request forgery (SSRF)
primitive: point it at ``http://127.0.0.1:8000`` or ``http://169.254.169.254`` and
the server happily fetches its own internals.

This module answers one question: *may we target this URL at all?* The scheme and
syntactic validity are already guaranteed by the ``HttpUrl`` type (a bad scheme is
a 422 before this code runs), so the checks here are about the host. Name
resolution is checked later, at navigation time (Day 3), because a DNS name can
resolve to a private address — and can be re-pointed between check and use. Every
redirect hop has to be re-checked for the same reason.

Only test sites you own or have explicit permission to test.
"""

import ipaddress

from pydantic import HttpUrl

from app.core.exceptions import InvalidTargetError

# Names that always mean "this machine" or a private network, regardless of DNS.
BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "ip6-localhost",
        "ip6-loopback",
        "metadata",  # cloud metadata hostnames (GCP/Azure style)
        "metadata.google.internal",
    }
)

# Suffixes that resolve inside a private or local network.
BLOCKED_HOST_SUFFIXES = (".localhost", ".local", ".internal", ".home.arpa", ".lan")


def assert_target_is_allowed(url: HttpUrl) -> None:
    """Raise :class:`InvalidTargetError` unless ``url`` targets a public host."""
    # Credentials in the URL are a common trick for hiding the real host
    # (``https://trusted.example@10.0.0.5/``) and we have no use for them.
    if url.username or url.password:
        raise InvalidTargetError("URLs with embedded credentials are not allowed.")

    host = _normalized_host(url)
    if not host:
        raise InvalidTargetError("The URL must include a hostname.")

    if host in BLOCKED_HOSTNAMES or host.endswith(BLOCKED_HOST_SUFFIXES):
        raise InvalidTargetError(f"Target host '{host}' is a local address and is not allowed.")

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        # A DNS name. It is checked again after resolution, before navigation.
        return

    if not address.is_global or address.is_multicast:
        raise InvalidTargetError(
            f"Target host '{host}' is a private, loopback or reserved address and is not allowed."
        )


def _normalized_host(url: HttpUrl) -> str:
    """Hostname in lowercase without IPv6 brackets or a trailing root dot."""
    host = (url.host or "").strip().lower().strip("[]")
    return host.rstrip(".")
