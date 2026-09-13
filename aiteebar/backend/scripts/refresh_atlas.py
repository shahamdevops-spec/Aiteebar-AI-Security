"""
Regenerate app/services/atlas/atlas_data.json from the authoritative
mitre-atlas/atlas-data repository.

Run this instead of hand-editing the JSON. ATLAS is revised regularly — v5.1.0
in November 2025 added a tactic and 18 techniques — and a stale or invented
AML.T#### in a SOC alert is worse than no mapping at all.

    python scripts/refresh_atlas.py

Afterwards, run the mapping validator, which fails loudly if a mapped
technique no longer exists:

    python -c "from app.services.atlas import mapping; print(mapping.validate() or 'ok')"
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

ATLAS_YAML_URL = "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml"
OUTPUT = Path(__file__).parent.parent / "app" / "services" / "atlas" / "atlas_data.json"

# ATLAS matrix column order. The YAML lists tactics in this order; we preserve
# it explicitly so a reordering upstream cannot silently scramble the matrix.
TACTIC_ORDER = [
    "AML.TA0002", "AML.TA0003", "AML.TA0004", "AML.TA0000",
    "AML.TA0005", "AML.TA0006", "AML.TA0012", "AML.TA0007",
    "AML.TA0013", "AML.TA0008", "AML.TA0015", "AML.TA0009",
    "AML.TA0001", "AML.TA0014", "AML.TA0010", "AML.TA0011",
]


def fetch() -> str:
    try:
        import httpx
    except ImportError:
        sys.exit("httpx is required: pip install httpx")

    print(f"fetching {ATLAS_YAML_URL}")
    response = httpx.get(ATLAS_YAML_URL, timeout=60, follow_redirects=True)
    response.raise_for_status()
    return response.text


def parse(raw: str) -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is required: pip install pyyaml")

    doc = yaml.safe_load(raw)

    # ATLAS.yaml nests everything under a matrix entry.
    matrices = doc.get("matrices") or []
    if not matrices:
        sys.exit("unexpected ATLAS.yaml shape: no 'matrices' key")
    matrix = matrices[0]

    tactics_by_id = {t["id"]: t["name"] for t in matrix.get("tactics", [])}

    ordered_tactics = [
        {"id": tid, "name": tactics_by_id[tid]}
        for tid in TACTIC_ORDER
        if tid in tactics_by_id
    ]
    # Anything new upstream that is not in TACTIC_ORDER still gets included,
    # appended rather than dropped silently.
    for tid, name in tactics_by_id.items():
        if tid not in TACTIC_ORDER:
            print(f"  note: tactic {tid} ({name}) is not in TACTIC_ORDER, appending")
            ordered_tactics.append({"id": tid, "name": name})

    base: dict = {}
    subs: dict = {}
    for technique in matrix.get("techniques", []):
        tid = technique["id"]
        if "subtechnique-of" in technique:
            subs.setdefault(technique["subtechnique-of"], []).append(
                {"id": tid, "name": technique["name"]}
            )
        else:
            base[tid] = {
                "id": tid,
                "name": technique["name"],
                "tactics": list(technique.get("tactics", [])),
                "subtechniques": [],
            }

    for parent_id, children in subs.items():
        if parent_id in base:
            base[parent_id]["subtechniques"] = sorted(children, key=lambda c: c["id"])
        else:
            print(f"  warning: sub-technique parent {parent_id} not found")

    # Emit techniques grouped by tactic order so the JSON reads like the matrix.
    emitted, seen = [], set()
    for tactic in ordered_tactics:
        for tid, technique in base.items():
            if tactic["id"] in technique["tactics"] and tid not in seen:
                emitted.append(technique)
                seen.add(tid)
    for tid, technique in base.items():
        if tid not in seen:
            print(f"  warning: {tid} ({technique['name']}) has no tactic, including anyway")
            emitted.append(technique)

    return {
        "source": "https://github.com/mitre-atlas/atlas-data (dist/ATLAS.yaml)",
        "retrieved": date.today().isoformat(),
        "note": (
            "MITRE ATLAS is updated regularly. Regenerate with "
            "scripts/refresh_atlas.py rather than editing this file by hand. "
            "Tactics are listed in matrix (kill-chain) order."
        ),
        "tactics": ordered_tactics,
        "techniques": emitted,
    }


def main() -> None:
    data = parse(fetch())

    previous = set()
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8") as fh:
            previous = {t["id"] for t in json.load(fh)["techniques"]}

    current = {t["id"] for t in data["techniques"]}

    with OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    subs = sum(len(t["subtechniques"]) for t in data["techniques"])
    print(f"\nwrote {OUTPUT.relative_to(Path(__file__).parent.parent)}")
    print(f"  {len(data['tactics'])} tactics, {len(current)} techniques, {subs} sub-techniques")

    if previous:
        added = current - previous
        removed = previous - current
        if added:
            print(f"  added:   {', '.join(sorted(added))}")
        if removed:
            # Removals matter most: a mapping pointing at a retired technique
            # must be revisited, not silently carried forward.
            print(f"  REMOVED: {', '.join(sorted(removed))}")
            print("  -> check app/services/atlas/mapping.py for references to these")
        if not added and not removed:
            print("  no technique changes")


if __name__ == "__main__":
    main()
