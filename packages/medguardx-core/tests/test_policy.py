"""Policy engine: correct strategies and deny-by-default for unmapped combos."""
from medguardx.enums import MaskingStrategy, Purpose, Role
from medguardx.policy import PolicyEngine


def setup_function():
    global engine
    engine = PolicyEngine()


def test_doctor_treatment_consent_is_full_access():
    strat, _ = engine.evaluate(Role.DOCTOR, Purpose.TREATMENT, True)
    assert strat == MaskingStrategy.FULL_ACCESS


def test_researcher_research_is_anonymized_regardless_of_consent():
    for consent in (True, False):
        strat, _ = engine.evaluate(Role.RESEARCHER, Purpose.RESEARCH, consent)
        assert strat == MaskingStrategy.FULL_ANONYMIZE


def test_unmapped_combination_is_denied():
    strat, rule = engine.evaluate(Role.COMPANY, Purpose.TREATMENT, False)
    assert strat == MaskingStrategy.DENY
    assert "denied" in rule.lower()


def test_accepts_plain_strings():
    strat, _ = engine.evaluate("nurse", "treatment", False)
    assert strat == MaskingStrategy.PARTIAL_MASK


def test_custom_rules_override_defaults():
    custom = {(Role.COMPANY, Purpose.TREATMENT, True): (MaskingStrategy.FULL_ACCESS, "custom")}
    e = PolicyEngine(rules=custom)
    strat, rule = e.evaluate(Role.COMPANY, Purpose.TREATMENT, True)
    assert strat == MaskingStrategy.FULL_ACCESS and rule == "custom"
    # anything else still deny-by-default
    assert e.evaluate(Role.DOCTOR, Purpose.TREATMENT, True)[0] == MaskingStrategy.DENY
