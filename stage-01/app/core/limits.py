"""
Centralized resource limits.

Defaults live here as plain constants (env-overridable) so every tool
module reads the same numbers. `LimitTracker` is the actual enforcement
point: it's a plain Python object bound to one ReconState/session, and
every network-capable tool must call its `check_*` methods *before*
doing work. The LLM never sees or controls this object directly — it
can only trigger tool calls, and the tools themselves refuse to exceed
these limits regardless of what the agent asks for.
"""

from __future__ import annotations

import os
import time

from .models import ReconLimits


def _env_int(name: str, default: int) -> int:
    val = os.getenv(name)
    return int(val) if val else default


DEFAULT_LIMITS = ReconLimits(
    max_requests=_env_int("MAX_REQUESTS", 5000),
    max_urls=_env_int("MAX_URLS", 10000),
    max_crawl_depth=_env_int("MAX_CRAWL_DEPTH", 5),
    max_concurrent_requests=_env_int("MAX_CONCURRENT_REQUESTS", 5),
    max_runtime_seconds=_env_int("MAX_RUNTIME_SECONDS", 1800),
)


class LimitExceeded(RuntimeError):
    def __init__(self, limit_name: str, limit_value: int):
        super().__init__(f"Limit '{limit_name}' exceeded (max {limit_value}).")
        self.limit_name = limit_name
        self.limit_value = limit_value


class LimitTracker:
    """
    Bound to a single ReconState. Tools call `check_*` before doing
    network work and `record_*` after. Raises LimitExceeded rather than
    silently clamping, so callers (tools) can turn that into a
    structured ToolError instead of a crash.
    """

    def __init__(self, limits: ReconLimits | None = None):
        self.limits = limits or DEFAULT_LIMITS
        self._requests = 0
        self._urls = 0
        self._started_at = time.monotonic()

    # --- checks (call before doing work) ---

    def check_runtime(self) -> None:
        elapsed = time.monotonic() - self._started_at
        if elapsed > self.limits.max_runtime_seconds:
            raise LimitExceeded("max_runtime_seconds", self.limits.max_runtime_seconds)

    def check_request_budget(self, n: int = 1) -> None:
        if self._requests + n > self.limits.max_requests:
            raise LimitExceeded("max_requests", self.limits.max_requests)

    def check_url_budget(self, n: int = 1) -> None:
        if self._urls + n > self.limits.max_urls:
            raise LimitExceeded("max_urls", self.limits.max_urls)

    def check_depth(self, depth: int) -> None:
        if depth > self.limits.max_crawl_depth:
            raise LimitExceeded("max_crawl_depth", self.limits.max_crawl_depth)

    # --- recording (call after doing work) ---

    def record_request(self, n: int = 1) -> None:
        self._requests += n

    def record_urls(self, n: int = 1) -> None:
        self._urls += n

    @property
    def elapsed_seconds(self) -> float:
        return time.monotonic() - self._started_at

    @property
    def requests_used(self) -> int:
        return self._requests

    @property
    def urls_used(self) -> int:
        return self._urls
