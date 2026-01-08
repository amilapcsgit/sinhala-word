"""Pytest configuration and shared fixtures."""
import pytest
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_sinhala_map():
    """Provide a sample Sinhala transliteration map for testing."""
    return {
        "mama": "මම",
        "api": "අපි",
        "oya": "ඔය",
        "kohomada": "කොහොමද",
        "ayubowan": "ආයුබෝවන්",
        "suba": "සුබ",
        "dawasa": "දවස",
    }


@pytest.fixture
def empty_map():
    """Provide an empty map for testing."""
    return {}
