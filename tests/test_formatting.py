import pytest

from app.core.formatting import format_message


def test_format_telegram_message() -> None:
    text = format_message("telegram", "Alert", "Body")
    assert "*Alert*" in text


def test_format_mattermost_message() -> None:
    text = format_message("mattermost", "Alert", "Body")
    assert text.startswith("### Alert")


def test_format_unknown_channel_raises_error() -> None:
    with pytest.raises(ValueError):
        format_message("unknown", "Alert", "Body")
