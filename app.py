"""CRREM Portfolio Assessment — Preview.

Streamlit demo in DPIM brand styling, four audience lenses.
Aesthetic: institutional research bulletin.

Run locally:
    streamlit run app.py
"""
from __future__ import annotations

import datetime as _dt

import streamlit as st

from crrem_core import rollup_ticker, rollup_portfolio
from data import TICKERS, EF_ANCHORS, PATHWAY_ANCHORS
from nzif import classify, portfolio_distribution
import lenses


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CRREM Portfolio Assessment — DPIM preview",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Fonts (separate <link> injections — Streamlit's HTML sanitiser strips
# <style> when combined with other head elements in one call)
# ---------------------------------------------------------------------------
st.markdown(
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    unsafe_allow_html=True,
)
st.markdown(
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    unsafe_allow_html=True,
)
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Roboto+Slab:wght@300;400;500;600;700&'
    'family=Open+Sans:wght@300;400;500;600;700&'
    'family=Spectral:ital,wght@0,400;0,500;1,400&'
    'family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# CSS — a plain string, CSS variables drive the palette
# ---------------------------------------------------------------------------
CSS = """
:root {
  --navy: #385676;
  --navy-deep: #243B5A;
  --ink: #0F1A24;
  --ink-soft: #1A2436;
  --maroon: #800000;
  --maroon-soft: #9A2F2C;
  --ochre: #B08D57;
  --ochre-soft: #C9A875;
  --sage: #6B8E6B;
  --rule: #D6D2C9;
  --rule-soft: #E4E0D6;
  --paper: #F5F1E8;
  --paper-soft: #FAF7EE;
  --paper-pale: #FCFAF5;
  --muted: #6B7281;
  --muted-soft: #8A8F99;
}

/* GLOBAL ---------------------------------------------------------------- */
html, body, [class*="css"], .stApp, .main {
  font-family: 'Open Sans', Helvetica, Arial, sans-serif !important;
  color: var(--ink) !important;
  background: var(--paper-pale) !important;
}
.stApp {
  background:
    radial-gradient(at 0% 0%, rgba(56, 86, 118, 0.025) 0%, transparent 35%),
    radial-gradient(at 100% 100%, rgba(128, 0, 0, 0.020) 0%, transparent 40%),
    var(--paper-pale) !important;
}
.main .block-container {
  padding-top: 1.4rem !important;
  padding-bottom: 4.5rem !important;
  max-width: 1280px !important;
}
h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
  font-family: 'Roboto Slab', Georgia, serif !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  letter-spacing: -0.012em !important;
}
p, li, .stMarkdown p, .stMarkdown li {
  font-size: 0.96rem;
  line-height: 1.6;
  color: var(--ink-soft);
}

/* MASTHEAD -------------------------------------------------------------- */
.masthead {
  border-top: 4px solid var(--navy);
  border-bottom: 1px solid var(--rule);
  padding: 1.1rem 0 0.95rem 0;
  margin-bottom: 0;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.masthead-left { display: flex; flex-direction: column; gap: 0.2rem; }
.masthead-eyebrow {
  font-family: 'Open Sans', sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--maroon);
  font-weight: 700;
}
.masthead-title {
  font-family: 'Roboto Slab', serif !important;
  font-size: 2.3rem;
  font-weight: 700 !important;
  color: var(--ink);
  line-height: 1.08;
  margin: 0.2rem 0 0.15rem 0;
  letter-spacing: -0.015em;
}
.masthead-sub {
  font-family: 'Spectral', Georgia, serif;
  font-style: italic;
  color: var(--muted);
  font-size: 1rem;
  font-weight: 400;
  letter-spacing: 0.005em;
}
.masthead-right {
  text-align: right;
  font-family: 'JetBrains Mono', SFMono-Regular, monospace;
  font-size: 0.7rem;
  color: var(--muted);
  letter-spacing: 0.08em;
  line-height: 1.7;
  text-transform: uppercase;
}

/* PREVIEW NOTICE -------------------------------------------------------- */
.preview-strip {
  background: var(--paper);
  border-left: 3px solid var(--maroon);
  padding: 0.75rem 1.1rem;
  margin: 1.1rem 0 1.6rem 0;
  font-size: 0.88rem;
  color: var(--ink-soft);
  line-height: 1.55;
}
.preview-strip b {
  font-family: 'Roboto Slab', serif;
  color: var(--maroon);
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  margin-right: 0.7rem;
  font-weight: 700;
}

/* STAT BAND ------------------------------------------------------------- */
.stat-band {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  margin: 0.4rem 0 0.6rem 0;
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--rule);
  background: var(--paper-pale);
}
.stat {
  padding: 1.2rem 1.3rem 1.25rem 1.3rem;
  border-right: 1px solid var(--rule);
  position: relative;
}
.stat:last-child { border-right: none; }
.stat-label {
  font-family: 'Open Sans', sans-serif;
  text-transform: uppercase;
  font-size: 0.66rem;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin-bottom: 0.55rem;
  font-weight: 600;
}
.stat-value {
  font-family: 'Roboto Slab', serif;
  font-size: 2.1rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.02em;
}
.stat-unit {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.45rem;
  letter-spacing: 0.04em;
  line-height: 1.4;
}
.stat-value.warn { color: var(--maroon); }
.stat-value.ok   { color: var(--sage); }

/* SECTION RULE ---------------------------------------------------------- */
.section-rule {
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  border-bottom: 1px solid var(--ink);
  padding-bottom: 0.4rem;
  margin: 2.6rem 0 1.1rem 0;
}
.section-rule .num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--maroon);
  letter-spacing: 0.16em;
  font-weight: 600;
}
.section-rule .ttl {
  font-family: 'Roboto Slab', serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.005em;
}

/* TICKER ROWS ----------------------------------------------------------- */
.ticker-row {
  display: grid;
  grid-template-columns: 90px 1.5fr 0.7fr 0.7fr 1.1fr 0.8fr;
  gap: 0.85rem;
  align-items: center;
  padding: 0.95rem 0.4rem;
  border-bottom: 1px solid var(--rule);
  transition: background 0.15s ease;
}
.ticker-row:hover { background: var(--paper-soft); }
.ticker-row.head {
  border-bottom: 1.5px solid var(--ink);
  padding-bottom: 0.6rem;
}
.ticker-row.head:hover { background: transparent; }
.ticker-row.head div {
  font-family: 'Open Sans', sans-serif;
  text-transform: uppercase;
  font-size: 0.66rem;
  letter-spacing: 0.2em;
  color: var(--muted);
  font-weight: 600;
}
.ticker-row .sym {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--navy);
  font-size: 0.95rem;
  letter-spacing: 0.04em;
}
.ticker-row .nm {
  font-family: 'Roboto Slab', serif;
  font-weight: 500;
  font-size: 0.99rem;
  color: var(--ink);
}
.ticker-row .nm small {
  display: block;
  font-family: 'Open Sans', sans-serif;
  font-weight: 400;
  color: var(--muted);
  font-size: 0.77rem;
  margin-top: 0.18rem;
  letter-spacing: 0.005em;
}
.ticker-row .num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.95rem;
  color: var(--ink);
  text-align: right;
  font-weight: 500;
}
.ticker-row .num small {
  font-family: 'Open Sans', sans-serif;
  font-size: 0.7rem;
  color: var(--muted);
  font-weight: 400;
  display: block;
  margin-top: 0.18rem;
  letter-spacing: 0.02em;
}

/* PILLS, DOTS ----------------------------------------------------------- */
.pill {
  display: inline-block;
  padding: 0.3rem 0.65rem;
  font-family: 'Open Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #FFFFFF;
  border-radius: 1px;
  white-space: nowrap;
  line-height: 1.2;
}
.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 0.5rem;
  vertical-align: middle;
}

/* LENS SELECTOR — newspaper-section tabs -------------------------------- */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
  flex-direction: row !important;
  gap: 0 !important;
  margin: 0.7rem 0 0 0 !important;
  border-top: 1px solid var(--rule) !important;
  border-bottom: 1px solid var(--ink) !important;
  background: var(--paper) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
  flex: 1 1 0 !important;
  margin: 0 !important;
  padding: 0.95rem 0.6rem 0.95rem 0.6rem !important;
  border-right: 1px solid var(--rule) !important;
  text-align: center !important;
  cursor: pointer !important;
  transition: all 0.18s ease-out !important;
  background: transparent !important;
  position: relative !important;
  min-height: 3.2rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:last-child {
  border-right: none !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
  display: none !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
  font-family: 'Roboto Slab', serif !important;
  font-weight: 500 !important;
  font-size: 0.95rem !important;
  color: var(--muted) !important;
  margin: 0 !important;
  white-space: nowrap !important;
  letter-spacing: -0.005em !important;
  line-height: 1.2 !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
  background: var(--paper-soft) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover p {
  color: var(--ink-soft) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
  background: var(--paper-pale) !important;
  border-bottom: 1px solid var(--paper-pale) !important;
  margin-bottom: -1px !important;
  z-index: 2;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked)::before {
  content: "";
  position: absolute;
  top: -1px; left: -1px; right: -1px;
  height: 3px;
  background: var(--maroon);
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
  color: var(--ink) !important;
  font-weight: 700 !important;
}

/* NZIF LEGEND (replaces inside-bar labels) ------------------------------ */
.nzif-legend {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0;
  margin-top: 1.1rem;
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
}
.nzif-legend .cell {
  padding: 0.85rem 1rem 0.95rem 1rem;
  border-right: 1px solid var(--rule);
  background: var(--paper-pale);
}
.nzif-legend .cell:last-child { border-right: none; }
.nzif-legend .swatch {
  width: 24px;
  height: 4px;
  margin-bottom: 0.55rem;
  border-radius: 0;
}
.nzif-legend .label {
  font-family: 'Roboto Slab', serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.005em;
  line-height: 1.25;
  min-height: 2.1rem;
}
.nzif-legend .pct {
  font-family: 'Roboto Slab', serif;
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.025em;
  line-height: 1;
  margin-top: 0.5rem;
}
.nzif-legend .pct small {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  font-weight: 400;
  margin-left: 0.25rem;
  letter-spacing: 0.04em;
}
.nzif-legend .count {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.4rem;
  letter-spacing: 0.04em;
}
.nzif-legend .cell.empty .label,
.nzif-legend .cell.empty .pct,
.nzif-legend .cell.empty .count { opacity: 0.35; }
.nzif-legend .cell.empty .swatch { opacity: 0.25; }

/* FOOTER ---------------------------------------------------------------- */
.footer-rule {
  margin-top: 3.5rem;
  padding-top: 1.1rem;
  border-top: 4px double var(--rule);
  font-size: 0.83rem;
  color: var(--muted);
  font-family: 'Spectral', Georgia, serif;
  line-height: 1.65;
  font-style: italic;
}
.footer-rule strong {
  font-style: normal;
  font-family: 'Roboto Slab', serif;
  color: var(--ink);
}

/* TABLES (Streamlit dataframe) ----------------------------------------- */
[data-testid="stDataFrame"] {
  border: 1px solid var(--rule) !important;
  border-radius: 0 !important;
}

/* STREAMLIT CHROME CLEANUP ---------------------------------------------- */
header[data-testid="stHeader"] { background: transparent !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.stDeployButton { display: none; }

/* SELECTBOX styling (drill-down) --------------------------------------- */
[data-testid="stSelectbox"] > div > div {
  border-radius: 0 !important;
  border-color: var(--rule) !important;
  background: var(--paper-pale) !important;
}

/* Make captions a bit more deliberate */
[data-testid="stCaptionContainer"] {
  font-family: 'Spectral', Georgia, serif !important;
  font-style: italic;
  color: var(--muted) !important;
  font-size: 0.86rem !important;
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------
@st.cache_data
def compute_portfolio():
    ticker_results = [rollup_ticker(t, EF_ANCHORS, PATHWAY_ANCHORS) for t in TICKERS]
    for t, raw in zip(ticker_results, TICKERS):
        cat, reasoning = classify(t["misalignment_year"], raw.nzif_inputs)
        t["nzif_category"] = cat
        t["nzif_reasoning"] = reasoning
    portfolio = rollup_portfolio(ticker_results)
    portfolio["nzif_distribution"] = portfolio_distribution(
        [(t["nzif_category"], t["total_gia_m2"]) for t in ticker_results]
    )
    return ticker_results, portfolio


ticker_results, portfolio = compute_portfolio()


# ---------------------------------------------------------------------------
# Masthead
# ---------------------------------------------------------------------------
today = _dt.date.today().strftime("%d %B %Y").upper()

st.markdown(
    f"""
<div class="masthead">
  <div class="masthead-left">
    <div class="masthead-eyebrow">Duff &amp; Phelps Investment Management · Preview</div>
    <div class="masthead-title">CRREM Portfolio Assessment</div>
    <div class="masthead-sub">Listed real-estate equities measured against the 1.5°C decarbonisation pathway</div>
  </div>
  <div class="masthead-right">
    Vol. I · No. 1<br>
    {today}<br>
    Methodology · CRREM v1.0 + NZIF
  </div>
</div>

<div class="preview-strip">
  <b>Preview</b>
  Inputs are illustrative — placeholder magnitudes chosen for demonstration.
  Replace each ticker's energy and disclosure inputs with figures from the
  issuer's most recent sustainability report before any decision use.
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Portfolio key figures
# ---------------------------------------------------------------------------
pf_mis = portfolio["misalignment_year"]
pf_mis_str = "Beyond 2050" if pf_mis == "Beyond 2050" else str(pf_mis)
pf_mis_warn = (
    pf_mis != "Beyond 2050" and int(pf_mis) <= 2035
    if pf_mis != "Beyond 2050"
    else False
)
n_aligned_or_better = sum(
    1 for t in ticker_results
    if t["nzif_category"] in ("Achieving Net Zero", "Aligned", "Aligning")
)
aligned_share = (
    sum(t["total_gia_m2"] for t in ticker_results
        if t["nzif_category"] in ("Achieving Net Zero", "Aligned", "Aligning"))
    / max(portfolio["total_gia_m2"], 1) * 100
)

st.markdown(
    f"""
<div class="stat-band">
  <div class="stat">
    <div class="stat-label">Holdings assessed</div>
    <div class="stat-value">{len(ticker_results)}</div>
    <div class="stat-unit">listed real-estate equities</div>
  </div>
  <div class="stat">
    <div class="stat-label">Portfolio carbon intensity</div>
    <div class="stat-value">{portfolio['carbon_intensity_kgco2_m2']:.1f}</div>
    <div class="stat-unit">kgCO₂e / m² · GIA-weighted · 2024</div>
  </div>
  <div class="stat">
    <div class="stat-label">Portfolio misalignment year</div>
    <div class="stat-value {'warn' if pf_mis_warn else 'ok'}">{pf_mis_str}</div>
    <div class="stat-unit">first year trajectory exceeds pathway</div>
  </div>
  <div class="stat">
    <div class="stat-label">NZIF aligning or better</div>
    <div class="stat-value">{aligned_share:.0f}%</div>
    <div class="stat-unit">{n_aligned_or_better} of {len(ticker_results)} holdings · % of GIA</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Lens selector
# ---------------------------------------------------------------------------
lens = st.radio(
    "Lens",
    ["Investment Committee", "Regulatory / LP", "Engagement", "Analyst"],
    horizontal=True,
    label_visibility="collapsed",
    key="lens_selector",
)

if lens == "Investment Committee":
    lenses.render_ic(ticker_results, portfolio)
elif lens == "Regulatory / LP":
    lenses.render_regulatory(ticker_results, portfolio, TICKERS)
elif lens == "Engagement":
    lenses.render_engagement(ticker_results, TICKERS)
else:
    lenses.render_analyst(ticker_results, TICKERS)


# ---------------------------------------------------------------------------
# Footer / colophon
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="footer-rule">
  <strong>Colophon.</strong>
  Methodology follows the CRREM Technical Blueprint v1.0
  (<a href="https://crrem.org/library/technical-blueprint" style="color:#385676;">crrem.org/library</a>)
  and the IIGCC Net Zero Investment Framework v2.0 — listed equity component plus the
  real-estate annex. Each issuer is modelled as a mini-portfolio of pseudo-assets carved by
  disclosed geographic and use-type segmentation; the CRREM compute then runs at pseudo-asset
  level and aggregates GIA-weighted to issuer and portfolio. Four audience-specific lenses
  present the same underlying model. Inputs in this preview are illustrative placeholders.
  Built for Duff &amp; Phelps Investment Management as a methodology demonstration.
</div>
""",
    unsafe_allow_html=True,
)
