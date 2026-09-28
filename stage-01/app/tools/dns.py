"""
DNS reconnaissance. TODO — implemented in Stage 4.

dns_lookup() will collect normal DNS records only (A, AAAA, CNAME, MX,
NS, TXT, CAA, SOA) for an in-scope target and return structured data,
recording each record as Evidence via the session's EvidenceStore.
No DNS attacks (zone transfer attempts, cache poisoning, etc.) — this
is read-only reconnaissance against public resolvers.
"""

from __future__ import annotations

from ..core.models import ToolError, ToolResult
from ..core.state import ReconSession


async def dns_lookup(session: ReconSession, target: str) -> ToolResult | ToolError:
    raise NotImplementedError("dns_lookup is implemented in Stage 4.")
