"""Compact CRREM-aligned compute engine for the preview demo.

Implements the CRREM Technical Blueprint v1.0 (asset Steps 1-6 and portfolio
Steps 1-4) at illustrative resolution. For the production build, swap the
illustrative reference data in `data.py` for the official CRREM Global Pathways
and Emission Factors datasets (open-access from crrem.org/library) and add
the validation suite against the four worked-example fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


CARRIERS = (
    "Elec_Grid", "Gas", "Oil", "District_Heating", "District_Cooling",
    "Biomass", "Other_Fuels", "Renew_Consumed",
)
PROJECTION_YEARS = range(2020, 2051)


@dataclass(frozen=True)
class PseudoAsset:
    """One country x one property-type sleeve of a listed REIT."""
    label: str
    country: str
    property_type: str
    gia_m2: float
    reporting_year: int
    energy_kwh: Mapping[str, float]
    renew_exported_kwh: float = 0.0


@dataclass(frozen=True)
class Ticker:
    """A listed REIT modeled as a mini-portfolio of pseudo-assets."""
    ticker: str
    name: str
    exchange: str
    pseudo_assets: list[PseudoAsset]
    disclosure_notes: str = ""
    nzif_inputs: Mapping[str, object] = field(default_factory=dict)


def _interp(anchors: Mapping[int, float], year: int) -> float:
    yrs = sorted(anchors.keys())
    if year <= yrs[0]:
        return anchors[yrs[0]]
    if year >= yrs[-1]:
        return anchors[yrs[-1]]
    for i in range(len(yrs) - 1):
        a, b = yrs[i], yrs[i + 1]
        if a <= year <= b:
            f = (year - a) / (b - a)
            return anchors[a] + f * (anchors[b] - anchors[a])
    return anchors[yrs[-1]]


def total_energy(pa: PseudoAsset) -> float:
    return sum(pa.energy_kwh.get(c, 0.0) for c in CARRIERS)


def eui(pa: PseudoAsset) -> float:
    return total_energy(pa) / pa.gia_m2


def ef_for(carrier: str, country: str, year: int, ef_anchors: dict) -> float:
    if carrier == "Renew_Consumed":
        return 0.0
    table = ef_anchors[carrier]
    anchors = table.get(country, table.get("__default__"))
    return _interp(anchors, year)


def carbon_intensity(pa: PseudoAsset, ef_anchors: dict, year: int | None = None) -> float:
    yr = year if year is not None else pa.reporting_year
    co2 = sum(
        pa.energy_kwh.get(c, 0.0) * ef_for(c, pa.country, yr, ef_anchors)
        for c in CARRIERS
    )
    ef_elec = ef_for("Elec_Grid", pa.country, yr, ef_anchors)
    raw_credit = pa.renew_exported_kwh * ef_elec
    cap = pa.energy_kwh.get("Elec_Grid", 0.0) * ef_elec
    credit = min(raw_credit, cap)
    return (co2 - credit) / pa.gia_m2


def pathway_for(country: str, ptype: str, year: int, pathway_anchors: dict) -> float:
    key = (country, ptype)
    if key not in pathway_anchors:
        key = ("__default__", ptype) if ("__default__", ptype) in pathway_anchors else None
    if key is None:
        return float("inf")
    return _interp(pathway_anchors[key], year)


def project_trajectory(pa: PseudoAsset, ef_anchors: dict) -> dict[int, float]:
    return {y: carbon_intensity(pa, ef_anchors, year=y) for y in PROJECTION_YEARS}


def project_pathway(pa: PseudoAsset, pathway_anchors: dict) -> dict[int, float]:
    return {y: pathway_for(pa.country, pa.property_type, y, pathway_anchors)
            for y in PROJECTION_YEARS}


def misalignment_year(traj: Mapping[int, float],
                      pathway: Mapping[int, float]) -> int | str:
    for y in sorted(traj.keys()):
        if traj[y] > pathway[y]:
            return y
    return "Beyond 2050"


def gia_weighted_trajectory(items: list[tuple[float, Mapping[int, float]]]
                            ) -> dict[int, float]:
    total = sum(g for g, _ in items)
    if total <= 0:
        return {}
    years = sorted(next(iter(items))[1].keys())
    return {y: sum((g / total) * t[y] for g, t in items) for y in years}


def rollup_ticker(t: Ticker, ef_anchors: dict, pathway_anchors: dict) -> dict:
    pas = []
    for pa in t.pseudo_assets:
        traj = project_trajectory(pa, ef_anchors)
        path = project_pathway(pa, pathway_anchors)
        pas.append({
            "label": pa.label,
            "gia_m2": pa.gia_m2,
            "country": pa.country,
            "property_type": pa.property_type,
            "eui_kwh_m2": eui(pa),
            "carbon_intensity_kgco2_m2": carbon_intensity(pa, ef_anchors),
            "trajectory": traj,
            "pathway": path,
            "misalignment_year": misalignment_year(traj, path),
        })
    traj = gia_weighted_trajectory([(p["gia_m2"], p["trajectory"]) for p in pas])
    path = gia_weighted_trajectory([(p["gia_m2"], p["pathway"]) for p in pas])
    total_gia = sum(p["gia_m2"] for p in pas)
    return {
        "ticker": t.ticker,
        "name": t.name,
        "exchange": t.exchange,
        "pseudo_assets": pas,
        "total_gia_m2": total_gia,
        "carbon_intensity_kgco2_m2": (
            sum(p["gia_m2"] * p["carbon_intensity_kgco2_m2"] for p in pas) / total_gia
            if total_gia else 0.0
        ),
        "trajectory": traj,
        "pathway": path,
        "misalignment_year": misalignment_year(traj, path),
        "disclosure_notes": t.disclosure_notes,
        "nzif_inputs": dict(t.nzif_inputs),
    }


def rollup_portfolio(tickers: list[dict]) -> dict:
    items_traj = [(t["total_gia_m2"], t["trajectory"]) for t in tickers]
    items_path = [(t["total_gia_m2"], t["pathway"]) for t in tickers]
    traj = gia_weighted_trajectory(items_traj)
    path = gia_weighted_trajectory(items_path)
    total_gia = sum(t["total_gia_m2"] for t in tickers)
    return {
        "total_gia_m2": total_gia,
        "carbon_intensity_kgco2_m2": (
            sum(t["total_gia_m2"] * t["carbon_intensity_kgco2_m2"] for t in tickers)
            / total_gia if total_gia else 0.0
        ),
        "trajectory": traj,
        "pathway": path,
        "misalignment_year": misalignment_year(traj, path),
    }
