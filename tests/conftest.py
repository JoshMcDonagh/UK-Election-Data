from __future__ import annotations

import sys
from pathlib import Path

import pytest


# The repository currently uses a src/ layout without packaging metadata.
# This lets the tests run directly from the repository root with `pytest`.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(autouse=True)
def clear_public_api_caches():
    """Keep tests independent of module-level election caches."""
    import uk_election_data

    uk_election_data._ge_cache.clear()
    uk_election_data._notional_ge_cache.clear()
    uk_election_data._all_ge_cache = None
    uk_election_data._all_ge_with_notional_cache = None

    yield

    uk_election_data._ge_cache.clear()
    uk_election_data._notional_ge_cache.clear()
    uk_election_data._all_ge_cache = None
    uk_election_data._all_ge_with_notional_cache = None
