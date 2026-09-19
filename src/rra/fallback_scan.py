"""Dependency-free public website fallback scanner for standalone MVP operation.

Hardened against SSRF: every hostname is resolved and every resolved IP is
checked against loopback/private/link-local/reserved/multicast ranges before
a connection is made. The connection is opened directly against the
validated IP (not re-resolved by the socket layer) to close the DNS-rebinding
TOCTOU gap, and redirects are followed manually with the same validation
applied to every hop.
"""
from __future__ import annotations

import ipaddress
import socket
import ssl
from html.parser import HTMLParser
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urljoin, urlparse

MAX_REDIRECTS = 5
MAX_BODY_BYTES = 2_000_000
ALLOWED_SCHEMES = {"http", "https"}


class _Signals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tel = False
        self.form = False
        self.schema = False
        self.booking = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        href = str(a.get('href', '')).lower()
        typ = str(a.get('type', '')).lower()
        if tag == 'a' and href.startswith('tel:'):
            self.tel = True
        if tag == 'form':
            self.form = True
        if tag == 'script' and typ == 'application/ld+json':
            self.schema = True
        if any(k in href for k in ('book', 'schedule', 'appointment')):
            self.booking = True


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ipaddress.IPv4Address(ip.ipv4_mapped)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_safe_ip(hostname: str, port: int) -> str:
    try:
        infos = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ValueError(f"could not resolve host: {hostname}") from exc
    if not infos:
        raise ValueError(f"could not resolve host: {hostname}")
    resolved_ip = None
    for family, _type, _proto, _canon, sockaddr in infos:
        addr = sockaddr[0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        if _is_blocked_ip(ip):
            raise ValueError(
                f"refusing to scan {hostname}: resolves to a non-public address ({addr})"
            )
        if resolved_ip is None:
            resolved_ip = str(addr)
    if resolved_ip is None:
        raise ValueError(f"could not resolve host: {hostname}")
    return resolved_ip


class _PinnedHTTPConnection(HTTPConnection):
    """HTTPConnection that connects to a pre-validated IP instead of re-resolving the host."""

    def __init__(self, host: str, pinned_ip: str, port: int, timeout: float):
        super().__init__(host, port, timeout=timeout)
        self._pinned_ip = pinned_ip

    def connect(self):
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)


class _PinnedHTTPSConnection(HTTPSConnection):
    """HTTPSConnection that connects to a pre-validated IP but keeps SNI/cert checks on the real host."""

    def __init__(self, host: str, pinned_ip: str, port: int, timeout: float):
        super().__init__(host, port, timeout=timeout)
        self._pinned_ip = pinned_ip

    def connect(self):
        raw_sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        context = self._context or ssl.create_default_context()
        self.sock = context.wrap_socket(raw_sock, server_hostname=self.host)


def _fetch_once(url: str, timeout: float) -> tuple[int, dict, bytes]:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        raise ValueError('url must be an absolute http(s) URL')

    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    pinned_ip = _resolve_safe_ip(parsed.hostname, port)

    path = parsed.path or '/'
    if parsed.query:
        path += f'?{parsed.query}'

    conn_cls = _PinnedHTTPSConnection if parsed.scheme == 'https' else _PinnedHTTPConnection
    conn = conn_cls(parsed.hostname, pinned_ip, port, timeout)
    try:
        conn.request('GET', path, headers={
            'User-Agent': 'RRA-MVP/1.0 public-audit',
            'Host': parsed.hostname,
        })
        resp = conn.getresponse()
        status = resp.status
        headers = dict(resp.getheaders())
        body = resp.read(MAX_BODY_BYTES)
        return status, headers, body
    finally:
        conn.close()


def scan_public_url(url: str, timeout: float = 12.0) -> str:
    current_url = url
    for _ in range(MAX_REDIRECTS + 1):
        status, headers, body = _fetch_once(current_url, timeout)
        if status in (301, 302, 303, 307, 308):
            location = headers.get('Location') or headers.get('location')
            if not location:
                raise ValueError('redirect response missing Location header')
            current_url = urljoin(current_url, location)
            continue
        ctype = (headers.get('Content-Type') or headers.get('content-type') or '').split(';')[0].strip().lower()
        if ctype not in {'text/html', 'application/xhtml+xml'}:
            raise ValueError(f'unsupported content type: {ctype}')
        text = body.decode('utf-8', errors='replace')
        p = _Signals()
        p.feed(text)
        signals = []
        if not p.tel:
            signals.append('no_click_to_call')
        if not p.form:
            signals.append('no_online_booking')
        if not p.booking:
            signals.append('no_online_booking')
        if not p.schema:
            signals.append('no_schema_markup')
        signals = list(dict.fromkeys(signals))
        return '\n'.join(f'- {s}' for s in signals)
    raise ValueError('too many redirects')
