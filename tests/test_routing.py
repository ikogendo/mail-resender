from app.core.router import route_channels


def test_route_critical_to_both_channels() -> None:
    assert route_channels("Critical incident") == ["telegram", "mattermost"]


def test_route_telegram_keyword() -> None:
    assert route_channels("telegram notification") == ["telegram"]


def test_route_default_to_mattermost() -> None:
    assert route_channels("daily report") == ["mattermost"]
