from services.search import core, providers


def _config(monkeypatch, settings):
    monkeypatch.setattr(core, "_get_search_settings", lambda: settings)
    monkeypatch.setattr(providers, "_get_search_settings", lambda: settings)
    return core.get_search_config()


def test_search_config_detects_active_provider_specific_key(monkeypatch):
    config = _config(monkeypatch, {
        "search_provider": "tavily",
        "tavily_api_key": "tavily-key",
    })

    assert config["has_api_key"] is True


def test_search_config_ignores_key_for_different_provider(monkeypatch):
    config = _config(monkeypatch, {
        "search_provider": "brave",
        "tavily_api_key": "tavily-key",
    })

    assert config["has_api_key"] is False


def test_search_config_keeps_legacy_shared_key_fallback(monkeypatch):
    config = _config(monkeypatch, {
        "search_provider": "serper",
        "search_api_key": "legacy-key",
    })

    assert config["has_api_key"] is True
