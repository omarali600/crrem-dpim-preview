# CRREM Portfolio Assessment — Preview

A single-page demonstration tool that measures a portfolio of listed
real-estate equities against the CRREM 1.5°C decarbonisation pathway,
classified through the IIGCC Net Zero Investment Framework (NZIF).

Built for Duff & Phelps Investment Management.

## What this preview shows

- **CRREM methodology applied to listed REITs.** Each ticker is modelled as a
  mini-portfolio of pseudo-assets carved by the issuer's disclosed
  geographic + use-type segmentation. CRREM compute runs at pseudo-asset
  level and aggregates GIA-weighted to issuer and portfolio.
- **Portfolio trajectory vs pathway**, 2020-2050, with the misalignment
  year (the first year the portfolio's flat-demand trajectory crosses the
  1.5°C pathway).
- **NZIF classification** per holding across the five categories —
  Achieving Net Zero / Aligned / Aligning / Committed to Aligning /
  Not Aligned.
- **Issuer drill-down** with per-pseudo-asset breakdown and reasoning behind
  the NZIF call.

## What this preview does NOT do

The five tickers (Land Securities, Unibail-Rodamco-Westfield, Prologis,
Vonovia, Segro) are real holdings but the **energy, GIA, and qualitative
NZIF inputs are illustrative placeholders**, not extractions from the
issuers' actual sustainability reports. Likewise, the CRREM pathways and
emission factors embedded in this preview are simplified approximations of
the published CRREM datasets — anchored on plausible magnitudes for the
relevant region × property type, linearly interpolated.

**Before using any number from this preview for a real decision**, replace
the inputs with values from each issuer's most recent sustainability
report, and swap the embedded reference data for the official CRREM Global
Pathways and Emission Factors datasets (open-access from
[crrem.org/library](https://crrem.org/library/pathways-and-datasets/)).

The accompanying spec and implementation plan describe the full production
system this preview points toward.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will open the app at <http://localhost:8501>.

## Files

```
app.py            — Streamlit page in DPIM brand styling
crrem_core.py     — Compact CRREM-aligned compute engine
nzif.py           — NZIF listed-equity classification decision tree
data.py           — The 5 tickers + illustrative pathway and EF anchors
.streamlit/config.toml — base theme
requirements.txt
```

## Methodology references

- CRREM Technical Blueprint v1.0 — <https://crrem.org/library/technical-blueprint>
- CRREM Pathways & Datasets — <https://crrem.org/library/pathways-and-datasets>
- IIGCC Net Zero Investment Framework — <https://www.iigcc.org/resource/net-zero-investment-framework-implementation-guide>
