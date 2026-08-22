#!/usr/bin/env python3
"""GLYPHLOCK reference runner.

GLYPHLOCK is a synthetic protocol invented purely as a foreign counterparty for
interoperability testing. It is not derived from WEXP, does not implement WEXP,
and its vocabulary deliberately has no shared roots with WEXP's.

It is also deliberately awkward: its wire format is line-oriented text rather
than JSON, its result algebra has a state with no analogue anywhere else, and it
refuses inputs that a JSON-shaped harness would find trivial. An interop
framework that can only talk to protocols shaped like itself has not been tested.

Run it standalone:

    python3 runner.py ward.glyph

Exit status: 0 if a seal state was determined, 3 if the format is unsupported,
4 if the request could not be parsed at all.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FORMAT = "GLYPHLOCK/1"
RESULT_FORMAT = "GLYPHLOCK-RESULT/1"

GLYPH_SEALED = "GLYPH_SEALED"
GLYPH_BROKEN = "GLYPH_BROKEN"
GLYPH_PARTIAL = "GLYPH_PARTIAL"
GLYPH_NO_ANALOGUE = "GLYPH_NO_ANALOGUE"
GLYPH_REFUSED = "GLYPH_REFUSED"

SIGIL = re.compile(r"^[0-9a-f]{8}$")
REQUIRED = ("warden", "ward-depth", "sigil", "chain", "epoch-band", "attest")


class GlyphError(Exception):
    """The ward request could not be parsed."""


class UnsupportedFormat(Exception):
    """This runner does not implement the declared format revision."""


def parse(text: str) -> dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise GlyphError("empty ward request")
    banner = lines[0]
    if not banner.startswith("GLYPHLOCK/"):
        raise GlyphError(f"not a ward request: {banner!r}")
    if banner != FORMAT:
        raise UnsupportedFormat(banner)
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if ":" not in line:
            raise GlyphError(f"malformed field line: {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        if key in fields:
            raise GlyphError(f"repeated field: {key}")
        fields[key] = value.strip()
    missing = [name for name in REQUIRED if name not in fields]
    if missing:
        raise GlyphError(f"missing field(s): {', '.join(missing)}")
    return fields


def appraise(fields: dict[str, str]) -> tuple[str, int, str]:
    """GLYPHLOCK's own algebra. It resembles nothing in particular on purpose."""

    if not SIGIL.fullmatch(fields["sigil"]):
        return GLYPH_REFUSED, 0, "sigil is not eight lowercase hex characters"

    chain = [link.strip() for link in fields["chain"].split("->") if link.strip()]
    if not chain:
        return GLYPH_REFUSED, 0, "chain is empty"

    try:
        depth = int(fields["ward-depth"])
    except ValueError:
        return GLYPH_REFUSED, 0, "ward-depth is not an integer"

    band = fields["epoch-band"]
    if ".." not in band:
        return GLYPH_REFUSED, 0, "epoch-band is not a range"
    low_text, _, high_text = band.partition("..")
    try:
        low, high = int(low_text), int(high_text)
    except ValueError:
        return GLYPH_REFUSED, 0, "epoch-band bounds are not integers"

    # GLYPHLOCK cares about whether the chain length falls inside a declared
    # epoch band. Nothing outside GLYPHLOCK models this, which is the point:
    # it produces a state a counterparty cannot mirror.
    if not low <= len(chain) <= high:
        return (
            GLYPH_NO_ANALOGUE, len(chain),
            f"chain length {len(chain)} lies outside epoch band {low}..{high}",
        )

    if fields["attest"] == "absent":
        return GLYPH_BROKEN, 0, "no attestation accompanies the ward"
    if fields["attest"] != "present":
        return GLYPH_REFUSED, 0, "attest must be present or absent"

    if depth > len(chain):
        return (
            GLYPH_PARTIAL, len(chain),
            f"ward depth {depth} exceeds the {len(chain)}-link chain",
        )
    return GLYPH_SEALED, depth, "ward reached its declared depth"


def render(state: str, reached: int, note: str) -> str:
    return (
        f"{RESULT_FORMAT}\n"
        f"seal-state: {state}\n"
        f"ward-reached: {reached}\n"
        f"notes: {note}\n"
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        sys.stderr.write("usage: runner.py WARD.glyph\n")
        return 4
    try:
        text = Path(argv[0]).read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"cannot read ward request: {exc}\n")
        return 4
    try:
        fields = parse(text)
    except UnsupportedFormat as exc:
        sys.stderr.write(f"unsupported ward format: {exc}\n")
        return 3
    except GlyphError as exc:
        sys.stderr.write(f"bad ward request: {exc}\n")
        return 4
    sys.stdout.write(render(*appraise(fields)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
