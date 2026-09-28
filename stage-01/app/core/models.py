"""
Core data models for ReconAgent.

Everything the rest of the app passes around — scope config, evidence
records, the recon state, structured tool errors — is a typed Pydantic
model here rather than a loose dict. Stage 1 only defines the shapes;
the tools that populate them arrive in later stages.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


# --------------------------------------------------------------------------
# Scope
# --------------------------------------------------------------------------


class ScopeConfig(BaseModel):
    """
    Authorization boundary for a recon session.

    `allowed` and `excluded` entries may be domains, subdomain wildcards
    (`*.example.com`), bare IPs, or CIDR ranges. Scope is never expanded
    automatically — see tools/scope.py (Stage 3) for matching rules.
    """

    allowed: list[str] = Field(default_factory=list)
    excluded: list[str] = Field(default_factory=list)


class ScopeDecision(BaseModel):
    """Result of checking one candidate target against a ScopeConfig."""

    target: str
    in_scope: bool
    reason: str
    matched_rule: str | None = None


# --------------------------------------------------------------------------
# Confidence
# --------------------------------------------------------------------------


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EvidenceQuality(str, Enum):
    """
    Used to label statements in the final report. Confidence (above)
    describes how sure we are of a specific observation; this describes
    the epistemic status of a claim built from one or more observations.
    """

    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"


# --------------------------------------------------------------------------
# Evidence
# --------------------------------------------------------------------------


class Evidence(BaseModel):
    """
    A single, concretely-observed fact. Evidence is never invented —
    every record here must trace back to a real tool execution.
    """

    id: str = Field(default_factory=lambda: new_id("obs"))
    target: str
    asset: str
    observation_type: str  # e.g. "dns_record", "http_header", "url"
    value: str
    source: str  # e.g. "DNS response", "HTTP response", "robots.txt"
    tool: str  # e.g. "dns_lookup", "http_probe"
    timestamp: float = Field(default_factory=time.time)
    confidence: Confidence
    raw_evidence: str | None = None  # short excerpt/snippet backing the claim


# --------------------------------------------------------------------------
# Assets discovered during recon
# --------------------------------------------------------------------------


class AssetKind(str, Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP = "ip"
    URL = "url"


class Asset(BaseModel):
    value: str
    kind: AssetKind
    first_seen: float = Field(default_factory=time.time)
    sources: list[str] = Field(default_factory=list)  # which tool(s) found it


class Technology(BaseModel):
    name: str
    category: str | None = None  # e.g. "web server", "CMS", "framework"
    version: str | None = None
    detected_via: str  # tool name
    confidence: Confidence = Confidence.MEDIUM


# --------------------------------------------------------------------------
# Resource limits
# --------------------------------------------------------------------------


class ReconLimits(BaseModel):
    max_requests: int = 5000
    max_urls: int = 10000
    max_crawl_depth: int = 5
    max_concurrent_requests: int = 5
    max_runtime_seconds: int = 1800


class ReconStatistics(BaseModel):
    requests: int = 0
    urls_discovered: int = 0
    tools_executed: int = 0
    started_at: float = Field(default_factory=time.time)
    elapsed_seconds: float = 0.0


# --------------------------------------------------------------------------
# Structured tool errors — every tool returns this shape on failure instead
# of raising, so one bad tool call never kills the whole recon session.
# --------------------------------------------------------------------------


class ToolErrorType(str, Enum):
    TIMEOUT = "TIMEOUT"
    CONNECTION_FAILURE = "CONNECTION_FAILURE"
    DNS_FAILURE = "DNS_FAILURE"
    TLS_ERROR = "TLS_ERROR"
    INVALID_TARGET = "INVALID_TARGET"
    REDIRECT_LOOP = "REDIRECT_LOOP"
    RATE_LIMITED = "RATE_LIMITED"
    HTTP_ERROR = "HTTP_ERROR"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    SCOPE_VIOLATION = "SCOPE_VIOLATION"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    UNKNOWN = "UNKNOWN"


class ToolError(BaseModel):
    success: Literal[False] = False
    error_type: ToolErrorType
    message: str
    target: str | None = None


class ToolResult(BaseModel):
    """Generic success envelope; `data` shape depends on the tool."""

    success: Literal[True] = True
    data: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------
# Recon state — the single source of truth for one recon session
# --------------------------------------------------------------------------


class ReconState(BaseModel):
    target: str
    scope: ScopeConfig
    assets: list[Asset] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    ips: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    technologies: list[Technology] = Field(default_factory=list)
    observations: list[Evidence] = Field(default_factory=list)
    limits: ReconLimits = Field(default_factory=ReconLimits)
    statistics: ReconStatistics = Field(default_factory=ReconStatistics)
    session_id: str = Field(default_factory=lambda: new_id("session"))
    created_at: float = Field(default_factory=time.time)
