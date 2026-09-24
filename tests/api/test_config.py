from app.core.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://user:password@localhost:5432/kairo",
        _env_file=None,
    )

    assert settings.app_name == "Kairo API"
    assert settings.environment == "development"
    assert settings.debug is False
