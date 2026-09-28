"""
Security header analysis. TODO — implemented in Stage 7.

analyze_security_headers() will check a probed response for
Strict-Transport-Security, Content-Security-Policy,
X-Content-Type-Options, X-Frame-Options, Referrer-Policy, and
Permissions-Policy, and record each as a neutral "security
configuration observation" — never an automatic "critical
vulnerability" verdict. Runs against data http_probe() already
collected; makes no new requests itself.
"""

from __future__ import annotations

from ..core.models import ToolError, ToolResult
from ..core.state import ReconSession


async def analyze_security_headers(session: ReconSession, url: str) -> ToolResult | ToolError:
    raise NotImplementedError("analyze_security_headers is implemented in Stage 7.")
