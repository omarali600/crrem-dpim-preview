"""Illustrative inputs for the preview.

These figures are PLACEHOLDERS chosen for orders of magnitude that resemble
listed REIT disclosures. They were NOT extracted from any specific sustainability
report. Replace each pseudo-asset's `energy_kwh`, `gia_m2`, and `nzif_inputs`
with values from the issuer's most recent sustainability report before any
decision use.

The preview's purpose is to demonstrate the methodology — pseudo-asset modeling
of a listed REIT, the CRREM compute, the NZIF classification, the portfolio
rollup — not to publish real assessments of the named tickers.
"""
from __future__ import annotations

from crrem_core import PseudoAsset, Ticker


# ---------------------------------------------------------------------------
# Illustrative CRREM 1.5°C pathways  (kgCO2e/m²/yr)
# Anchored on typical magnitudes for the relevant region × property type.
# Production build: replace with the official CRREM Global Pathways dataset.
# ---------------------------------------------------------------------------
PATHWAY_ANCHORS: dict[tuple[str, str], dict[int, float]] = {
    ("UK", "Office"):           {2020: 55.0, 2030: 22.0, 2040: 9.0,  2050: 3.0},
    ("UK", "Retail"):           {2020: 47.0, 2030: 19.0, 2040: 7.5,  2050: 2.5},
    ("UK", "Logistics"):        {2020: 30.0, 2030: 12.0, 2040: 4.5,  2050: 1.5},
    ("FR", "Retail"):           {2020: 30.0, 2030: 12.0, 2040: 4.0,  2050: 1.5},
    ("FR", "Office"):           {2020: 38.0, 2030: 15.0, 2040: 6.0,  2050: 2.0},
    ("DE", "Residential"):      {2020: 42.0, 2030: 16.0, 2040: 6.5,  2050: 2.2},
    ("DE", "Logistics"):        {2020: 32.0, 2030: 13.0, 2040: 5.0,  2050: 1.7},
    ("US", "Logistics"):        {2020: 48.0, 2030: 19.0, 2040: 7.0,  2050: 2.3},
}


# ---------------------------------------------------------------------------
# Illustrative emission factors  (kgCO2e/kWh)
# Grid factors decline with national decarbonisation trajectories.
# Production build: replace with the official CRREM Emission Factors dataset.
# ---------------------------------------------------------------------------
EF_ANCHORS: dict[str, dict[str, dict[int, float]]] = {
    "Elec_Grid": {
        "UK": {2020: 0.210, 2030: 0.095, 2040: 0.040, 2050: 0.020},
        "FR": {2020: 0.060, 2030: 0.030, 2040: 0.015, 2050: 0.005},
        "DE": {2020: 0.360, 2030: 0.150, 2040: 0.060, 2050: 0.020},
        "US": {2020: 0.390, 2030: 0.220, 2040: 0.100, 2050: 0.040},
    },
    "Gas":              {"__default__": {2020: 0.202, 2050: 0.202}},
    "Oil":              {"__default__": {2020: 0.281, 2050: 0.281}},
    "District_Heating": {"__default__": {2020: 0.205, 2050: 0.205}},
    "District_Cooling": {"__default__": {2020: 0.060, 2050: 0.060}},
    "Biomass":          {"__default__": {2020: 0.018, 2050: 0.018}},
    "Other_Fuels":      {"__default__": {2020: 0.250, 2050: 0.250}},
}


# ---------------------------------------------------------------------------
# Five tickers — illustrative pseudo-asset segmentation.
# Geographic + use-type splits reflect the kind of structure these REITs
# typically disclose. Energy magnitudes are placeholders.
# ---------------------------------------------------------------------------
TICKERS: list[Ticker] = [
    Ticker(
        ticker="LAND.L",
        name="Land Securities Group",
        exchange="LSE",
        disclosure_notes=(
            "UK REIT. Typically reports a Central London Office portfolio and a "
            "Retail / Outlets sleeve with whole-building energy disclosure."
        ),
        pseudo_assets=[
            PseudoAsset(
                label="Central London Office",
                country="UK", property_type="Office",
                gia_m2=590_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 65_000_000, "Gas": 18_000_000,
                            "District_Heating": 4_500_000},
                renew_exported_kwh=900_000,
            ),
            PseudoAsset(
                label="UK Retail & Outlets",
                country="UK", property_type="Retail",
                gia_m2=410_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 42_000_000, "Gas": 9_500_000},
            ),
        ],
        nzif_inputs={
            "net_zero_commitment": True,
            "sbti_validated": True,
            "short_term_target": True,
            "medium_term_target": True,
            "decarbonization_capex_plan": True,
            "board_climate_oversight": True,
            "remuneration_link": True,
            "disclosure_quality": "high",
        },
    ),
    Ticker(
        ticker="URW.PA",
        name="Unibail-Rodamco-Westfield",
        exchange="Euronext Paris",
        disclosure_notes=(
            "Pan-European retail. Pseudo-asset split by major country exposures; "
            "energy reported portfolio-wide with regional breakdowns."
        ),
        pseudo_assets=[
            PseudoAsset(
                label="France Retail",
                country="FR", property_type="Retail",
                gia_m2=1_200_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 215_000_000, "District_Heating": 22_000_000,
                            "District_Cooling": 18_000_000, "Gas": 12_000_000},
            ),
            PseudoAsset(
                label="UK Retail (Westfield London / Stratford)",
                country="UK", property_type="Retail",
                gia_m2=320_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 58_000_000, "Gas": 6_500_000},
            ),
        ],
        nzif_inputs={
            "net_zero_commitment": True,
            "sbti_validated": True,
            "short_term_target": True,
            "medium_term_target": True,
            "decarbonization_capex_plan": True,
            "board_climate_oversight": True,
            "remuneration_link": False,
            "disclosure_quality": "high",
        },
    ),
    Ticker(
        ticker="PLD",
        name="Prologis",
        exchange="NYSE",
        disclosure_notes=(
            "US-led global logistics. Pseudo-asset confined to US logistics sleeve "
            "for the preview; production build adds EU/JP/MX sleeves."
        ),
        pseudo_assets=[
            PseudoAsset(
                label="US Logistics",
                country="US", property_type="Logistics",
                gia_m2=6_500_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 410_000_000, "Gas": 38_000_000},
                renew_exported_kwh=58_000_000,
            ),
        ],
        nzif_inputs={
            "net_zero_commitment": True,
            "sbti_validated": True,
            "short_term_target": True,
            "medium_term_target": True,
            "decarbonization_capex_plan": True,
            "board_climate_oversight": True,
            "remuneration_link": True,
            "disclosure_quality": "high",
        },
    ),
    Ticker(
        ticker="VNA.DE",
        name="Vonovia",
        exchange="Xetra",
        disclosure_notes=(
            "Large-cap German residential. Single-country, single-use sleeve. "
            "Residential portfolio dominated by district heating and gas."
        ),
        pseudo_assets=[
            PseudoAsset(
                label="Germany Residential",
                country="DE", property_type="Residential",
                gia_m2=29_500_000, reporting_year=2024,
                energy_kwh={"District_Heating": 4_100_000_000, "Gas": 2_800_000_000,
                            "Elec_Grid": 380_000_000, "Oil": 95_000_000},
            ),
        ],
        nzif_inputs={
            "net_zero_commitment": True,
            "sbti_validated": False,
            "short_term_target": True,
            "medium_term_target": True,
            "decarbonization_capex_plan": True,
            "board_climate_oversight": True,
            "remuneration_link": False,
            "disclosure_quality": "medium",
        },
    ),
    Ticker(
        ticker="SGRO.L",
        name="Segro",
        exchange="LSE",
        disclosure_notes=(
            "UK-listed, UK + Continental Europe logistics. Two pseudo-assets "
            "for UK and DE sleeves."
        ),
        pseudo_assets=[
            PseudoAsset(
                label="UK Logistics",
                country="UK", property_type="Logistics",
                gia_m2=2_900_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 95_000_000, "Gas": 6_500_000},
                renew_exported_kwh=8_500_000,
            ),
            PseudoAsset(
                label="Germany Logistics",
                country="DE", property_type="Logistics",
                gia_m2=1_400_000, reporting_year=2024,
                energy_kwh={"Elec_Grid": 48_000_000, "Gas": 4_200_000},
            ),
        ],
        nzif_inputs={
            "net_zero_commitment": True,
            "sbti_validated": True,
            "short_term_target": True,
            "medium_term_target": False,
            "decarbonization_capex_plan": True,
            "board_climate_oversight": True,
            "remuneration_link": True,
            "disclosure_quality": "high",
        },
    ),
]
