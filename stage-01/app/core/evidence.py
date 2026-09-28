"""
Evidence handling.

The rule this module exists to enforce: nothing becomes an Evidence
record unless a real tool actually observed it. There is no path here
that lets the agent "assert" an observation without a backing tool
result — `EvidenceStore.record()` is the only way an Evidence object
gets created, and every call site is a tool module (Stage 3+).
"""

from __future__ import annotations

from .models import Confidence, Evidence, ReconState


def create_evidence(
    *,
    target: str,
    asset: str,
    observation_type: str,
    value: str,
    source: str,
    tool: str,
    confidence: Confidence,
    raw_evidence: str | None = None,
) -> Evidence:
    return Evidence(
        target=target,
        asset=asset,
        observation_type=observation_type,
        value=value,
        source=source,
        tool=tool,
        confidence=confidence,
        raw_evidence=raw_evidence,
    )


class EvidenceStore:
    """Bound to one ReconState; appends and (later) queries evidence."""

    def __init__(self, state: ReconState):
        self._state = state

    def record(
        self,
        *,
        asset: str,
        observation_type: str,
        value: str,
        source: str,
        tool: str,
        confidence: Confidence,
        raw_evidence: str | None = None,
    ) -> Evidence:
        ev = create_evidence(
            target=self._state.target,
            asset=asset,
            observation_type=observation_type,
            value=value,
            source=source,
            tool=tool,
            confidence=confidence,
            raw_evidence=raw_evidence,
        )
        self._state.observations.append(ev)
        return ev

    def all(self) -> list[Evidence]:
        return list(self._state.observations)

    def for_asset(self, asset: str) -> list[Evidence]:
        return [e for e in self._state.observations if e.asset == asset]

    def for_tool(self, tool: str) -> list[Evidence]:
        return [e for e in self._state.observations if e.tool == tool]
