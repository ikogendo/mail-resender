from app.core.dedup import Deduplicator


def test_dedup_marks_second_occurrence_as_duplicate() -> None:
    dedup = Deduplicator()
    assert dedup.is_duplicate("msg-1") is False
    assert dedup.is_duplicate("msg-1") is True
