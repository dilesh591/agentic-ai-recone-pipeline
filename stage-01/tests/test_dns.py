"""
Tests for app.tools.dns. Placeholder — dns_lookup() is a Stage 4 stub.
Real tests (record parsing, DNS failure handling) land in Stage 10,
using mocked resolver responses rather than live third-party lookups.
"""

import pytest


def test_dns_not_yet_implemented():
    pytest.skip("dns_lookup is implemented in Stage 4; tests land in Stage 10.")
