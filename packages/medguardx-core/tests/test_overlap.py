"""Overlap resolution: a specialized entity must beat a generic one deterministically."""
from medguardx.detection import PIIEntity, resolve_overlaps


def _ent(etype, start, end, score):
    return PIIEntity(entity_type=etype, start=start, end=end, score=score, text="x")


def test_phone_beats_datetime_even_at_lower_score():
    # The exact failure from the old build: DATE_TIME(0.85) shadowed PHONE(0.75).
    ents = [_ent("DATE_TIME", 0, 10, 0.85), _ent("PHONE_NUMBER", 0, 10, 0.75)]
    out = resolve_overlaps(ents)
    assert len(out) == 1
    assert out[0].entity_type == "PHONE_NUMBER"


def test_aadhaar_beats_datetime():
    ents = [_ent("DATE_TIME", 5, 19, 0.85), _ent("IN_AADHAAR", 5, 19, 0.9)]
    out = resolve_overlaps(ents)
    assert len(out) == 1 and out[0].entity_type == "IN_AADHAAR"


def test_email_beats_overlapping_url():
    ents = [_ent("URL", 10, 21, 0.5), _ent("EMAIL_ADDRESS", 5, 21, 1.0)]
    out = resolve_overlaps(ents)
    assert len(out) == 1 and out[0].entity_type == "EMAIL_ADDRESS"


def test_non_overlapping_entities_all_kept_and_sorted():
    ents = [_ent("PERSON", 20, 30, 0.9), _ent("PHONE_NUMBER", 0, 10, 0.8)]
    out = resolve_overlaps(ents)
    assert [e.entity_type for e in out] == ["PHONE_NUMBER", "PERSON"]
    assert out[0].start < out[1].start


def test_deterministic_same_input_same_output():
    ents = [_ent("DATE_TIME", 0, 10, 0.85), _ent("PHONE_NUMBER", 0, 10, 0.75)]
    assert resolve_overlaps(list(ents)) == resolve_overlaps(list(reversed(ents)))
