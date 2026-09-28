"""
Unit tests for app.core.limits — this module is fully implemented in
Stage 1 (unlike the tool stubs), so it gets real tests now rather than
waiting for Stage 10.
"""

import pytest

from app.core.limits import LimitExceeded, LimitTracker
from app.core.models import ReconLimits


def _tracker(**overrides) -> LimitTracker:
    limits = ReconLimits(**overrides)
    return LimitTracker(limits)


def test_request_budget_allows_within_limit():
    t = _tracker(max_requests=10)
    t.check_request_budget(5)
    t.record_request(5)
    assert t.requests_used == 5


def test_request_budget_raises_when_exceeded():
    t = _tracker(max_requests=3)
    t.record_request(3)
    with pytest.raises(LimitExceeded):
        t.check_request_budget(1)


def test_url_budget_raises_when_exceeded():
    t = _tracker(max_urls=1)
    t.record_urls(1)
    with pytest.raises(LimitExceeded):
        t.check_url_budget(1)


def test_depth_limit_raises_when_exceeded():
    t = _tracker(max_crawl_depth=2)
    t.check_depth(2)  # exactly at the limit is fine
    with pytest.raises(LimitExceeded):
        t.check_depth(3)


def test_runtime_limit_not_exceeded_immediately():
    t = _tracker(max_runtime_seconds=60)
    t.check_runtime()  # should not raise right after construction
