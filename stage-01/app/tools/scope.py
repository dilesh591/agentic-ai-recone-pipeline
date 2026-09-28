"""
Scope validation. TODO — implemented in Stage 3.

validate_scope() will accept a candidate target (domain, subdomain, IP,
or CIDR) plus a ScopeConfig, and return a ScopeDecision. It must:

- match `allowed` entries (domain, `*.example.com` wildcard, bare IP, CIDR)
- reject anything matching `excluded`, even if also matched by `allowed`
- reject anything matching neither
- never expand scope automatically because a discovered asset "looks related"

This is the gate every other tool calls before touching a target.
"""

from __future__ import annotations

from ..core.models import ScopeConfig, ScopeDecision


def validate_scope(target: str, scope: ScopeConfig) -> ScopeDecision:
    raise NotImplementedError("validate_scope is implemented in Stage 3.")
