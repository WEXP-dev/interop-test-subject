# interop-test-subject — GLYPHLOCK

Synthetic foreign-system material only. Nothing else belongs here.

GLYPHLOCK is a protocol invented purely to act as a counterparty in
interoperability testing. It is not derived from WEXP, does not implement WEXP,
and shares no vocabulary with it. It is not used by anyone, anywhere, for
anything.

It is deliberately awkward. Its wire format is line-oriented text rather than
JSON, its result algebra contains a state with no analogue in any other system,
and it refuses inputs a JSON-shaped harness would find trivial. A framework that
can only talk to protocols shaped like itself has not been tested.

## Running it

No framework, no dependencies, no installation:

```sh
python3 glyphlock/runner.py fixtures/G-001-sealed.glyph
```

Exit status: `0` a seal state was determined · `3` unsupported format revision ·
`4` the request could not be parsed.

## Result algebra

| State | Meaning |
|---|---|
| `GLYPH_SEALED` | The ward reached its declared depth |
| `GLYPH_BROKEN` | No attestation accompanies the ward |
| `GLYPH_PARTIAL` | Ward depth exceeds the chain — GLYPHLOCK cannot decide |
| `GLYPH_NO_ANALOGUE` | Chain length falls outside the declared epoch band |
| `GLYPH_REFUSED` | The request is malformed |

`GLYPH_NO_ANALOGUE` is the interesting one. Nothing outside GLYPHLOCK models
epoch bands, so no counterparty can mirror that state — which is the point.

## Fixtures

| File | Produces |
|---|---|
| `G-001-sealed.glyph` | `GLYPH_SEALED` |
| `G-002-broken.glyph` | `GLYPH_BROKEN` |
| `G-003-partial.glyph` | `GLYPH_PARTIAL` |
| `G-004-no-analogue.glyph` | `GLYPH_NO_ANALOGUE` |
| `G-005-hostile.glyph` | a hostile twin of G-001 |
| `G-006-unsupported.glyph` | exit 3 — this runner implements `GLYPHLOCK/1` only |

## What is not here

No generic interop core. No adapters. No WEXP material. No production
semantics. Those live elsewhere; this repository is the counterparty and
nothing more.

## Status and licence

**Synthetic test fixture / synthetic counterparty.** GLYPHLOCK exists to be the
other party in an interoperability exercise and nothing else. It is not a WEXP
implementation, not a supported third-party system, not a standards artifact,
not a product, and not external validation of anything.

Licensed under the Apache License, Version 2.0 — see [`LICENSE`](LICENSE).
Every file here was written for this repository. No background material is
carried in, and nothing here relicenses anything else.
