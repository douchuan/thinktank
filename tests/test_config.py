from hundred_schools.config import Settings


def test_settings_uses_default_model_when_unset(monkeypatch) -> None:
    monkeypatch.delenv("MODEL", raising=False)
    settings = Settings.from_env()
    assert settings.model
