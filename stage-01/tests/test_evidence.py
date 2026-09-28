"""
Unit tests for app.core.evidence and the ReconSession it's bound to.
"""

from app.core.evidence import create_evidence
from app.core.models import AssetKind, Confidence, ScopeConfig
from app.core.state import ReconSession


def test_create_evidence_shape():
    ev = create_evidence(
        target="example.com",
        asset="example.com",
        observation_type="http_header",
        value="max-age=31536000",
        source="HTTP response",
        tool="http_probe",
        confidence=Confidence.HIGH,
    )
    assert ev.target == "example.com"
    assert ev.confidence == Confidence.HIGH
    assert ev.id.startswith("obs-")


def test_evidence_store_records_and_queries():
    session = ReconSession(target="example.com", scope=ScopeConfig(allowed=["example.com"]))
    session.evidence.record(
        asset="example.com",
        observation_type="dns_record",
        value="203.0.113.10",
        source="DNS response",
        tool="dns_lookup",
        confidence=Confidence.HIGH,
    )
    assert len(session.evidence.all()) == 1
    assert len(session.evidence.for_tool("dns_lookup")) == 1
    assert len(session.evidence.for_tool("http_probe")) == 0


def test_recon_session_add_asset_dedupes_and_tracks_sources():
    session = ReconSession(target="example.com", scope=ScopeConfig(allowed=["example.com"]))
    session.add_asset("example.com", AssetKind.DOMAIN, source="dns_lookup")
    session.add_asset("example.com", AssetKind.DOMAIN, source="http_probe")

    assert len(session.state.assets) == 1
    assert session.state.assets[0].sources == ["dns_lookup", "http_probe"]
    assert session.state.domains == ["example.com"]


def test_missing_information_reports_everything_missing_initially():
    session = ReconSession(target="example.com", scope=ScopeConfig(allowed=["example.com"]))
    missing = session.missing_information()
    assert "dns_reconnaissance" in missing
    assert "http_reconnaissance" in missing
    assert "url_discovery" in missing
    assert "security_header_analysis" in missing
