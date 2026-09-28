"""
HTTP/HTTPS reconnaissance. TODO — implemented in Stage 5.

http_probe() will fetch a single URL (GET, no form submission, no
auth-bypass attempts, no server-state changes) and record: status
code, redirect chain, content type, server header, response size,
a fixed set of security headers, and TLS info where available.
Must respect the session's LimitTracker (request budget, rate limit,
timeout) and refuse anything validate_scope() rejects.
"""

from __future__ import annotations

from ..core.models import ToolError, ToolResult
from ..core.state import ReconSession


async def http_probe(session: ReconSession, url: str) -> ToolResult | ToolError:
    raise NotImplementedError("http_probe is implemented in Stage 5.")
