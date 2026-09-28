"""
Final JSON report generation. TODO — implemented in Stage 9.

generate_json_report() will assemble a ReconSession's state into the
report shape from the spec: scan / scope / assets / dns / http / urls /
observations / statistics / limitations, explicitly labeling each claim
as Observed, Inferred, or Unverified. No new tool calls happen here —
this only serializes what's already in ReconState/EvidenceStore.
"""

from __future__ import annotations

from ..core.state import ReconSession


def generate_json_report(session: ReconSession) -> dict:
    raise NotImplementedError("generate_json_report is implemented in Stage 9.")
