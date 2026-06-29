from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from api import load_config  # noqa: E402


def test_config_loads_api_base():
    config = load_config()
    assert config["api_base"] == "http://127.0.0.1:18080"


def test_users_endpoint_missing_from_config():
    config = load_config()
    assert "users_endpoint" not in config