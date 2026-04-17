from pathlib import Path

from app.config import load_config


def test_load_from_toml(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text(
        """
app_name = "custom"
sqlite_path = "/tmp/test.db"
log_dir = "/tmp/logs"
polling_interval_seconds = 10
secret_key = "abc"
profiling_enabled = true
metrics_enabled = false
timezone = "Europe/Berlin"

[flask]
host = "127.0.0.1"
port = 9000

[retry_policy]
max_retries = 5
backoff_seconds = 2.5
""".strip()
    )

    cfg = load_config(cfg_file)

    assert cfg.app_name == "custom"
    assert cfg.flask.port == 9000
    assert cfg.retry_policy.max_retries == 5


def test_env_overrides(monkeypatch, tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text('app_name = "from-file"')

    monkeypatch.setenv("MAILBRIDGE_APP_NAME", "from-env")
    monkeypatch.setenv("MAILBRIDGE_FLASK_PORT", "5001")

    cfg = load_config(cfg_file)

    assert cfg.app_name == "from-env"
    assert cfg.flask.port == 5001
