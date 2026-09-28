"""
ReconSession wraps one ReconState with the objects that mutate it
safely: a LimitTracker (Stage-1 resource enforcement) and an
EvidenceStore (append-only observation log). Tool modules (Stage 3+)
receive a ReconSession, not a bare dict, so every mutation goes through
a typed method here instead of ad-hoc dictionary writes.
"""

from __future__ import annotations

from .evidence import EvidenceStore
from .limits import DEFAULT_LIMITS, LimitTracker
from .models import (
    Asset,
    AssetKind,
    ReconLimits,
    ReconState,
    ScopeConfig,
    Technology,
)


class ReconSession:
    def __init__(
        self,
        target: str,
        scope: ScopeConfig,
        limits: ReconLimits | None = None,
    ):
        self.state = ReconState(target=target, scope=scope, limits=limits or DEFAULT_LIMITS)
        self.limiter = LimitTracker(self.state.limits)
        self.evidence = EvidenceStore(self.state)

    # --- asset bookkeeping -------------------------------------------------

    def add_asset(self, value: str, kind: AssetKind, source: str) -> Asset:
        existing = next((a for a in self.state.assets if a.value == value), None)
        if existing:
            if source not in existing.sources:
                existing.sources.append(source)
            return existing

        asset = Asset(value=value, kind=kind, sources=[source])
        self.state.assets.append(asset)

        if kind in (AssetKind.DOMAIN, AssetKind.SUBDOMAIN) and value not in self.state.domains:
            self.state.domains.append(value)
        elif kind is AssetKind.IP and value not in self.state.ips:
            self.state.ips.append(value)
        elif kind is AssetKind.URL and value not in self.state.urls:
            self.state.urls.append(value)
            self.state.statistics.urls_discovered += 1

        return asset

    def add_technology(self, tech: Technology) -> None:
        existing = next(
            (t for t in self.state.technologies if t.name == tech.name and t.detected_via == tech.detected_via),
            None,
        )
        if existing is None:
            self.state.technologies.append(tech)

    # --- statistics ----------------------------------------------------

    def mark_tool_executed(self) -> None:
        self.state.statistics.tools_executed += 1

    def sync_statistics(self) -> None:
        self.state.statistics.requests = self.limiter.requests_used
        self.state.statistics.elapsed_seconds = self.limiter.elapsed_seconds

    # --- planning helpers (used by the agent to decide what's left) ----

    def missing_information(self) -> list[str]:
        """
        Cheap, deterministic checklist of recon aspects not yet attempted.
        This is intentionally simple in Stage 1 — it just reports what
        hasn't been populated yet, not what *should* be. The agent uses
        this alongside its own judgment once tools exist (Stage 8).
        """
        missing = []
        if not self.state.domains and not self.state.ips:
            missing.append("dns_reconnaissance")
        if not any(e.tool == "http_probe" for e in self.state.observations):
            missing.append("http_reconnaissance")
        if not self.state.urls:
            missing.append("url_discovery")
        if not any(e.observation_type == "http_header" for e in self.state.observations):
            missing.append("security_header_analysis")
        return missing

    def should_stop(self) -> tuple[bool, str]:
        self.sync_statistics()
        if self.limiter.elapsed_seconds > self.state.limits.max_runtime_seconds:
            return True, "max_runtime_seconds reached"
        if not self.missing_information():
            return True, "sufficient information collected"
        return False, ""

    def summary(self) -> dict:
        return {
            "target": self.state.target,
            "session_id": self.state.session_id,
            "domains": len(self.state.domains),
            "ips": len(self.state.ips),
            "urls": len(self.state.urls),
            "technologies": len(self.state.technologies),
            "observations": len(self.state.observations),
            "tools_executed": self.state.statistics.tools_executed,
            "elapsed_seconds": round(self.limiter.elapsed_seconds, 2),
        }
