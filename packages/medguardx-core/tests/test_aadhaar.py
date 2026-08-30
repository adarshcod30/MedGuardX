"""Aadhaar recognizer: Verhoeff-valid numbers score high; junk is rejected."""
from medguardx.recognizers.aadhaar import AadhaarRecognizer, _verhoeff_valid


def _run(text):
    return AadhaarRecognizer().analyze(text, entities=["IN_AADHAAR"])


def test_verhoeff_known_valid_and_invalid():
    # 234123412346 has a valid Verhoeff check digit; flipping it invalidates.
    assert _verhoeff_valid("234123412346")
    assert not _verhoeff_valid("234123412340")


def test_detects_spaced_aadhaar():
    res = _run("Aadhaar 2341 2341 2346 on record")
    assert len(res) == 1
    assert res[0].entity_type == "IN_AADHAAR"
    assert res[0].score >= 0.9  # valid checksum -> high confidence


def test_detects_bare_twelve_digit_aadhaar():
    # The exact case the old build missed entirely (returned nothing).
    res = _run("ID 234123412346 filed")
    assert len(res) == 1 and res[0].entity_type == "IN_AADHAAR"


def test_shape_match_without_valid_checksum_still_flagged_lower():
    res = _run("Number 234123412340 here")
    assert len(res) == 1
    assert 0.4 <= res[0].score < 0.9


def test_ignores_non_aadhaar_numbers():
    assert _run("Call 9305597756 today") == []  # 10 digits, not Aadhaar-shaped


def test_does_not_match_inside_a_credit_card():
    # 16-digit card must NOT be picked up as a 12-digit Aadhaar.
    assert _run("card 4111 1111 1111 1111 on file") == []
    assert _run("4111111111111111") == []
