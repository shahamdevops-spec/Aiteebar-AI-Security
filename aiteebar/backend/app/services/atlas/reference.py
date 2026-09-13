"""
MITRE ATLAS reference data.

Loaded from atlas_data.json, which is generated from the authoritative
mitre-atlas/atlas-data repository. Refresh with scripts/refresh_atlas.py; do
not hand-edit technique IDs, because a wrong AML.T#### in a SOC alert is worse
than no mapping at all.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).parent / "atlas_data.json"


@lru_cache(maxsize=1)
def _load() -> Dict[str, Any]:
    with DATA_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def provenance() -> Dict[str, str]:
    """Where this data came from and when, so consumers can judge staleness."""
    data = _load()
    return {
        "source": data["source"],
        "retrieved": data["retrieved"],
        "note": data["note"],
    }


@lru_cache(maxsize=1)
def tactics() -> List[Dict[str, str]]:
    """Tactics in ATLAS matrix (kill-chain) order."""
    return list(_load()["tactics"])


@lru_cache(maxsize=1)
def techniques() -> List[Dict[str, Any]]:
    """All base techniques, each carrying its sub-techniques."""
    return list(_load()["techniques"])


@lru_cache(maxsize=1)
def _technique_index() -> Dict[str, Dict[str, Any]]:
    """Every technique and sub-technique by id, for O(1) lookup."""
    index: Dict[str, Dict[str, Any]] = {}
    for technique in techniques():
        index[technique["id"]] = technique
        for sub in technique.get("subtechniques", []):
            index[sub["id"]] = {
                **sub,
                "tactics": technique["tactics"],
                "parent": technique["id"],
                "subtechniques": [],
            }
    return index


@lru_cache(maxsize=1)
def _tactic_index() -> Dict[str, Dict[str, str]]:
    return {tactic["id"]: tactic for tactic in tactics()}


def get_technique(technique_id: str) -> Optional[Dict[str, Any]]:
    """Look up a technique or sub-technique by id. None if unknown."""
    return _technique_index().get(technique_id)


def get_tactic(tactic_id: str) -> Optional[Dict[str, str]]:
    return _tactic_index().get(tactic_id)


def technique_name(technique_id: str) -> str:
    technique = get_technique(technique_id)
    return technique["name"] if technique else "Unknown technique"


def is_valid_technique(technique_id: str) -> bool:
    """Guard against a typo'd id silently entering an alert."""
    return technique_id in _technique_index()


def describe(technique_id: str) -> Dict[str, Any]:
    """
    Expand a technique id into the shape used in API responses and SIEM
    payloads: id, name, and the tactics it belongs to.
    """
    technique = get_technique(technique_id)
    if not technique:
        return {"id": technique_id, "name": "Unknown technique", "tactics": []}

    return {
        "id": technique_id,
        "name": technique["name"],
        "tactics": [
            {"id": tactic_id, "name": (get_tactic(tactic_id) or {}).get("name", tactic_id)}
            for tactic_id in technique.get("tactics", [])
        ],
        "url": f"https://atlas.mitre.org/techniques/{technique_id}",
    }


def techniques_for_tactic(tactic_id: str) -> List[Dict[str, Any]]:
    """Base techniques assigned to a tactic, in data order."""
    return [t for t in techniques() if tactic_id in t.get("tactics", [])]


def counts() -> Dict[str, int]:
    all_techniques = techniques()
    return {
        "tactics": len(tactics()),
        "techniques": len(all_techniques),
        "subtechniques": sum(len(t.get("subtechniques", [])) for t in all_techniques),
    }
