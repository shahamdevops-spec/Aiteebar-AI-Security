"""
MITRE ATLAS API endpoints.

Exposes the ATLAS matrix, this platform's coverage of it, and the mapping
between Aiteebar detections and ATLAS techniques.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.services.atlas import mapping, reference

router = APIRouter(prefix="/api/atlas", tags=["atlas"])


@router.get("")
async def atlas_summary():
    """Framework version, counts, and headline coverage."""
    cov = mapping.coverage()
    return {
        "framework": "MITRE ATLAS",
        "provenance": reference.provenance(),
        "counts": reference.counts(),
        "coverage": {
            "covered": cov["covered_count"],
            "total": cov["total_techniques"],
            "percent": cov["coverage_percent"],
        },
    }


@router.get("/tactics")
async def list_tactics():
    """ATLAS tactics in matrix (kill-chain) order."""
    covered = mapping.covered_technique_ids()
    return [
        {
            **tactic,
            "technique_count": len(reference.techniques_for_tactic(tactic["id"])),
            "covered_count": sum(
                1 for t in reference.techniques_for_tactic(tactic["id"])
                if t["id"] in covered
            ),
        }
        for tactic in reference.tactics()
    ]


@router.get("/matrix")
async def get_matrix():
    """
    The full ATLAS matrix with a detected flag on every technique.

    This is the view that answers "what can this platform actually see?" —
    including, deliberately, everything it cannot.
    """
    covered = mapping.covered_technique_ids()

    return {
        "provenance": reference.provenance(),
        "tactics": [
            {
                **tactic,
                "techniques": [
                    {
                        "id": technique["id"],
                        "name": technique["name"],
                        "detected": technique["id"] in covered,
                        "subtechnique_count": len(technique.get("subtechniques", [])),
                    }
                    for technique in reference.techniques_for_tactic(tactic["id"])
                ],
            }
            for tactic in reference.tactics()
        ],
    }


@router.get("/coverage")
async def get_coverage():
    """Coverage broken down per tactic, with the uncovered count made explicit."""
    cov = mapping.coverage()
    return {
        **cov,
        "by_tactic": [
            {
                "tactic_id": row["tactic"]["id"],
                "tactic_name": row["tactic"]["name"],
                "total": row["total"],
                "covered": row["covered"],
                "uncovered": row["total"] - row["covered"],
                "percent": round(row["covered"] / row["total"] * 100, 1) if row["total"] else 0.0,
                "covered_ids": row["covered_ids"],
            }
            for row in cov["by_tactic"]
        ],
    }


@router.get("/mappings")
async def get_mappings():
    """
    Which Aiteebar detection maps to which ATLAS technique, and why.

    Each entry carries a confidence and a rationale so a reviewer can
    challenge an individual claim rather than the table as a whole.
    """
    return {
        "threat_rules": {
            rule: mapping.for_rule(rule) for rule in mapping.RULE_MAPPINGS
        },
        "dlp_data_types": {
            data_type: mapping.for_data_type(data_type) for data_type in mapping.DLP_MAPPINGS
        },
        "event_types": {
            event_type: mapping.for_event_type(event_type) for event_type in mapping.EVENT_MAPPINGS
        },
    }


# Declared before /techniques/{technique_id} so the literal path is not
# captured as an id.
@router.get("/techniques")
async def list_techniques(
    tactic: Optional[str] = Query(None, description="Filter to one tactic, e.g. AML.TA0010"),
    detected_only: bool = Query(False, description="Only techniques this platform detects"),
):
    """All ATLAS techniques, optionally filtered."""
    covered = mapping.covered_technique_ids()
    results = reference.techniques_for_tactic(tactic) if tactic else reference.techniques()

    if tactic and not results and not reference.get_tactic(tactic):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown tactic {tactic}",
        )

    if detected_only:
        results = [t for t in results if t["id"] in covered]

    return [
        {
            **reference.describe(technique["id"]),
            "detected": technique["id"] in covered,
            "subtechniques": technique.get("subtechniques", []),
        }
        for technique in results
    ]


@router.get("/techniques/{technique_id}")
async def get_technique(technique_id: str):
    """
    One technique or sub-technique, with the detections that cover it.

    `detected_by` is empty when nothing in the platform covers it — which is
    the honest answer for 50 of the 59 techniques.
    """
    technique = reference.get_technique(technique_id)
    if not technique:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown ATLAS technique {technique_id}",
        )

    detected_by = [
        {"detection": rule, "type": "threat_rule", "confidence": entry["confidence"],
         "rationale": entry["rationale"]}
        for rule in mapping.RULE_MAPPINGS
        for entry in mapping.for_rule(rule)
        if entry["id"] == technique_id
    ] + [
        {"detection": data_type, "type": "dlp_data_type", "confidence": entry["confidence"],
         "rationale": entry["rationale"]}
        for data_type in mapping.DLP_MAPPINGS
        for entry in mapping.for_data_type(data_type)
        if entry["id"] == technique_id
    ]

    return {
        **reference.describe(technique_id),
        "subtechniques": technique.get("subtechniques", []),
        "detected": technique_id in mapping.covered_technique_ids(),
        "detected_by": detected_by,
    }
