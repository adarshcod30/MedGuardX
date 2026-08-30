# medguardx-core

Context-aware **PII/PHI detection and masking** for healthcare data — a stateless,
model-configurable, framework-agnostic Python engine. This is the reusable core of
[MedGuardX](https://github.com/adarshcod30/MedGuardX); embed it in any project.

## Why

- **Stateless & safe to embed** — text and context in, masked text out. No auth, no
  database, no global state. Your app owns storage, identity, and audit.
- **Bring your own model** — any installed spaCy English pipeline works
  (`en_core_web_sm` / `md` / `lg` / `trf`). Pick your accuracy/RAM trade-off.
- **Model-independent structured IDs** — Aadhaar (Verhoeff-validated), PAN, MRN,
  credit cards, IBAN, IP are matched by format, so they work identically on every
  model.
- **Deterministic, leak-proof masking** — overlapping detections are resolved by a
  fixed priority, and no strategy ever leaves part of a detected identifier visible.

## Install

```bash
pip install medguardx-core
python -m spacy download en_core_web_md   # recommended default
# other options: en_core_web_sm (smallest) · en_core_web_lg (best statistical)
# for the transformer model: pip install "medguardx-core[trf]" && python -m spacy download en_core_web_trf
```

The engine is model-agnostic — install any spaCy English pipeline and pass its name
to `EngineConfig(model=...)`. (Model wheels aren't declared as dependencies because
spaCy models aren't on PyPI; `spacy download` is the standard way to fetch them.)

## Quickstart

```python
from medguardx import MedGuardEngine, EngineConfig, Role, Purpose

engine = MedGuardEngine(EngineConfig(model="en_core_web_md"))

result = engine.process(
    "Patient John Smith, Aadhaar 2341 2341 2346, card 4111 1111 1111 1111.",
    role=Role.NURSE, purpose=Purpose.TREATMENT, consent=False,
)

print(result.masking_strategy if False else result.strategy.value)  # partial_mask
print(result.masked_text)
# Patient [NAME_REDACTED], Aadhaar [AADHAAR_REDACTED], card [CARD ****1111].
```

Compose the steps yourself when you need to:

```python
entities = engine.detect(text)                       # list[PIIEntity]
strategy, rule = engine.evaluate_policy(Role.DOCTOR, Purpose.RESEARCH, consent=False)
masked = engine.mask(text, entities, strategy)
```

## Configuration

`EngineConfig(model=..., score_threshold=..., entities=[...], enable_custom_recognizers=True)`.

`DATE_TIME` is intentionally **not** in the default entity set — as a high-confidence
span it used to shadow phone numbers and Aadhaar. Add it back explicitly if you need
date masking.

## Custom policy

```python
from medguardx import PolicyEngine, MedGuardEngine, Role, Purpose, MaskingStrategy

rules = {(Role.COMPANY, Purpose.TREATMENT, True): (MaskingStrategy.PARTIAL_MASK, "vendor SLA")}
engine = MedGuardEngine(policy=PolicyEngine(rules=rules))   # deny-by-default for the rest
```

## Masking strategies

| Strategy | Behaviour |
|---|---|
| `full_access` | text returned unchanged |
| `partial_mask` | identifiers redacted; card/phone/email keep a minimal safe hint |
| `full_anonymize` | every identifier replaced with a typed `[TYPE_REDACTED]` token |
| `deny` | access refused; no data returned |

## Ingestion (optional)

`medguardx.ingestion.extract_text(filename, bytes)` pulls text from plain text, PDF
(`pdfplumber`), images (`pytesseract`), and HL7 (`hl7apy`). Those extractors import
their heavy deps lazily.

## License

Apache-2.0.
