"""Masking must never leak the original substring (the old build's core bug)."""
from medguardx.detection import PIIEntity
from medguardx.enums import MaskingStrategy
from medguardx.masking import mask_text


def _ent(text, start, etype, score=0.9):
    return PIIEntity(entity_type=etype, start=start, end=start + len(text), score=score, text=text)


def test_full_access_returns_text_unchanged():
    txt = "Card 4111 1111 1111 1111"
    ents = [_ent("4111 1111 1111 1111", 5, "CREDIT_CARD")]
    assert mask_text(txt, ents, MaskingStrategy.FULL_ACCESS) == txt


def test_full_anonymize_removes_every_entity_substring():
    txt = "IP 192.168.1.55 and IBAN DE89370400440532013000 here."
    ents = [_ent("192.168.1.55", 3, "IP_ADDRESS"), _ent("DE89370400440532013000", 25, "IBAN_CODE")]
    out = mask_text(txt, ents, MaskingStrategy.FULL_ANONYMIZE)
    assert "192.168.1.55" not in out
    assert "DE89370400440532013000" not in out
    assert "[IP_REDACTED]" in out and "[IBAN_REDACTED]" in out


def test_partial_card_reveals_only_last_four():
    txt = "Card 4111111111111111 on file"
    ents = [_ent("4111111111111111", 5, "CREDIT_CARD")]
    out = mask_text(txt, ents, MaskingStrategy.PARTIAL_MASK)
    assert "4111111111111111" not in out
    assert "1111" in out  # last 4 kept for utility
    assert out.count("1") == 4  # nothing else from the PAN survives


def test_partial_ip_and_iban_are_fully_redacted_not_leaked():
    # These have no partial operator -> must be fully redacted, unlike the old
    # build which left "********1.55" and "********00440532013000".
    txt = "IP 192.168.1.55, IBAN DE89370400440532013000"
    ents = [_ent("192.168.1.55", 3, "IP_ADDRESS"), _ent("DE89370400440532013000", 22, "IBAN_CODE")]
    out = mask_text(txt, ents, MaskingStrategy.PARTIAL_MASK)
    assert "1.55" not in out
    assert "440532013000" not in out


def test_deny_returns_denied_placeholder_only():
    out = mask_text("secret", [], MaskingStrategy.DENY)
    assert "secret" not in out and "DENIED" in out.upper()


def test_stale_span_is_skipped_not_crashing():
    txt = "short"
    ents = [_ent("this is longer than the text", 0, "PERSON")]
    # end past len(text): span skipped rather than corrupting output
    assert mask_text(txt, ents, MaskingStrategy.FULL_ANONYMIZE) == txt
