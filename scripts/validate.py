#!/usr/bin/env python3
"""Validate data/fees.json against the schema and flag implausible rates.

Usage:  python scripts/validate.py [path/to/fees.json]

Exits non-zero on any error, so it can be wired straight into CI.
Requires: jsonschema  (pip install jsonschema)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "fees.json"
SCHEMA = ROOT / "schema" / "fees.schema.json"

# A taker fee above this is almost certainly a unit error (percent entered as
# a decimal fraction, or basis points entered raw). 0.5% is already generous
# for a centralised venue at VIP0.
IMPLAUSIBLE_ABOVE = 0.005


def main() -> int:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    errors, warnings = [], []

    try:
        import jsonschema
    except ImportError:
        warnings.append("jsonschema not installed - skipping schema validation "
                        "(pip install jsonschema)")
    else:
        if not hasattr(jsonschema, "Draft202012Validator"):
            warnings.append("jsonschema is too old for draft 2020-12 - skipping "
                            "schema validation (pip install -U 'jsonschema>=4.18')")
        else:
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator(schema)
            for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
                errors.append(f"schema: {'/'.join(map(str, err.path))}: {err.message}")

    seen = set()
    for ex in doc.get("exchanges", []):
        eid = ex.get("id", "<missing id>")

        if eid in seen:
            errors.append(f"{eid}: duplicate exchange id")
        seen.add(eid)

        if ex.get("verified_at") != doc.get("snapshot_date"):
            warnings.append(
                f"{eid}: verified_at {ex.get('verified_at')} differs from "
                f"snapshot_date {doc.get('snapshot_date')}"
            )

        for market in ("spot", "futures"):
            block = ex.get(market)
            if not block:
                continue
            for tier, rates in block.items():
                maker, taker = rates.get("maker"), rates.get("taker")
                for label, val in (("maker", maker), ("taker", taker)):
                    if val is None:
                        continue
                    if val > IMPLAUSIBLE_ABOVE:
                        errors.append(
                            f"{eid}.{market}.{tier}.{label} = {val} "
                            f"- above {IMPLAUSIBLE_ABOVE}. Rates are decimal "
                            f"fractions: 0.05% is 0.0005, not 0.05."
                        )
                if maker is not None and taker is not None and maker > taker:
                    warnings.append(
                        f"{eid}.{market}.{tier}: maker {maker} > taker {taker} "
                        f"- unusual, confirm against the source page."
                    )

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\n{len(errors)} error(s). Not ready to merge.")
        return 1

    n = len(doc.get("exchanges", []))
    print(f"\nOK - {n} venues, snapshot {doc.get('snapshot_date')}, "
          f"{len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
