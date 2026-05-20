"""NZIF (Net Zero Investment Framework) — illustrative listed-equity classification.

Five categories per IIGCC NZIF guidance:
  - Achieving Net Zero
  - Aligned
  - Aligning
  - Committed to Aligning
  - Not Aligned

This is the preview's deterministic decision tree. The production build pins
a specific NZIF guidance version in config and draws on the NZIF real-estate
annex alongside the listed-equity criteria.
"""
from __future__ import annotations

from typing import Mapping


CATEGORIES = (
    "Achieving Net Zero",
    "Aligned",
    "Aligning",
    "Committed to Aligning",
    "Not Aligned",
)

CATEGORY_COLOR = {
    "Achieving Net Zero":     "#385676",  # DPIM navy — strongest alignment
    "Aligned":                "#6B8E6B",  # muted sage
    "Aligning":               "#B08D57",  # ochre
    "Committed to Aligning":  "#A67C52",  # darker ochre
    "Not Aligned":            "#800000",  # DPIM heritage maroon — risk
}

CATEGORY_RANK = {c: i for i, c in enumerate(CATEGORIES)}


def _qualitative_score(inputs: Mapping[str, object]) -> int:
    keys = (
        "net_zero_commitment",
        "sbti_validated",
        "short_term_target",
        "medium_term_target",
        "decarbonization_capex_plan",
        "board_climate_oversight",
        "remuneration_link",
    )
    return sum(1 for k in keys if inputs.get(k))


def classify(misalignment_year: int | str,
             nzif_inputs: Mapping[str, object]) -> tuple[str, list[str]]:
    """Return (category, reasoning_bullets).

    The decision tree:
      1. Misaligned today and disclosure low → Not Aligned.
      2. Trajectory crosses pathway after 2050 + all qualitative checks +
         high disclosure → Achieving Net Zero.
      3. Misalignment year >= 2045 + strong qualitative + high disclosure → Aligned.
      4. Misalignment year >= 2035 + net-zero commitment + medium-term target +
         disclosure medium or high → Aligning.
      5. Net-zero commitment present + at least one target +
         misalignment year >= 2028 → Committed to Aligning.
      6. Otherwise → Not Aligned.
    """
    quality = nzif_inputs.get("disclosure_quality", "low")
    q_score = _qualitative_score(nzif_inputs)
    reasoning: list[str] = []

    beyond = misalignment_year == "Beyond 2050"
    year = 9999 if beyond else int(misalignment_year)

    reasoning.append(
        f"CRREM misalignment year: {'Beyond 2050' if beyond else year}"
    )
    reasoning.append(f"Qualitative checks met: {q_score} of 7")
    reasoning.append(f"Disclosure quality: {quality}")

    if beyond and q_score >= 6 and quality == "high":
        reasoning.append(
            "Trajectory remains below the 1.5°C pathway through 2050 with all "
            "qualitative NZIF criteria met; classified as the strongest category."
        )
        return "Achieving Net Zero", reasoning

    if (beyond or year >= 2045) and q_score >= 5 and quality == "high":
        reasoning.append(
            "Long pathway runway and strong qualitative signals support Aligned."
        )
        return "Aligned", reasoning

    if year >= 2035 and nzif_inputs.get("net_zero_commitment") and \
       nzif_inputs.get("medium_term_target") and quality in ("medium", "high"):
        reasoning.append(
            "Misalignment beyond 2035 with net-zero commitment, medium-term target, "
            "and acceptable disclosure quality."
        )
        return "Aligning", reasoning

    if nzif_inputs.get("net_zero_commitment") and (
        nzif_inputs.get("short_term_target") or nzif_inputs.get("medium_term_target")
    ) and year >= 2028:
        reasoning.append(
            "Net-zero commitment and at least one interim target, but CRREM "
            "misalignment is earlier than NZIF expects for Aligning."
        )
        return "Committed to Aligning", reasoning

    reasoning.append(
        "Insufficient combination of CRREM alignment, targets, and disclosure "
        "for any category above Not Aligned."
    )
    return "Not Aligned", reasoning


def portfolio_distribution(per_ticker: list[tuple[str, float]]) -> dict[str, float]:
    """Aggregate (category, weight) tuples into % share per category."""
    total = sum(w for _, w in per_ticker)
    out = {c: 0.0 for c in CATEGORIES}
    if total <= 0:
        return out
    for cat, w in per_ticker:
        out[cat] = out.get(cat, 0.0) + (w / total) * 100.0
    return out
