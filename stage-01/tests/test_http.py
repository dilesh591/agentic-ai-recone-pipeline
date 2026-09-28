"""
Tests for app.tools.http. Placeholder — http_probe() is a Stage 5
stub. Real tests (response parsing, redirect handling, timeout /
connection-failure structured errors) land in Stage 10, using mocked
HTTP responses rather than live third-party requests.
"""

import pytest


def test_http_not_yet_implemented():
    pytest.skip("http_probe is implemented in Stage 5; tests land in Stage 10.")
