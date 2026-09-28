"""
Public URL discovery. TODO — implemented in Stage 6.

discover_urls() will initially cover robots.txt, sitemap.xml, and links
scraped from publicly accessible HTML (no JS execution, no form
submission). Every discovered URL must pass validate_scope() before
being followed, and the tool must respect MAX_URLS, MAX_CRAWL_DEPTH,
and the session's rate limit. External domains are recorded but never
auto-followed.
"""

from __future__ import annotations

from ..core.models import ToolError, ToolResult
from ..core.state import ReconSession


async def discover_urls(session: ReconSession, start_url: str, max_depth: int = 2) -> ToolResult | ToolError:
    raise NotImplementedError("discover_urls is implemented in Stage 6.")
