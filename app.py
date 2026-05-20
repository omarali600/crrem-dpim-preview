"""CRREM Portfolio Assessment — Preview.

Streamlit demo in DPIM brand styling, four audience lenses.

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
# Inject fonts and CSS — separated to avoid markdown swallowing the style block
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

# CSS as a plain string — CSS variables do the colour substitution, not f-strings,
# so there's no brace-escaping issue.
CSS = """
:root {
  --navy: #385676;
  --navy-deep: #243B5A;
  --ink: #1A2436;
  --maroon: #800000;
  --ochre: #B08D57;
  --sage: #6B8E6B;
  --rule: #C8CCD2;
  --paper: #F5F3EE;
  --paper-soft: #FBFAF6;
  --muted: #5C6473;
}

html, body, [class*="css"], .stApp, .main {
  font-family: 'Open Sans', Helvetica, Arial, sans-serif !important;
  color: var(--ink) !important;
  background: #FFFFFF !important;
}
.stApp { background: #FFFFFF !important; }
.main .block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 4rem !important;
  max-width: 1280px !important;
}

h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
  font-family: 'Roboto Slab', Georgia, serif !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em !important;
}

p, li, .stMarkdown p, .stMarkdown li {
  font-size: 0.96rem;
  line-height: 1.55;
  color: var(--ink);
}

/* MASTHEAD --------------------------------------------------------------- */
.masthead {
  border-top: 3px solid var(--navy);
  border-bottom: 1px solid var(--rule);
  padding: 1rem 0 0.9rem 0;
  margin-bottom: 0.3rem;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.masthead-left { display: flex; flex-direction: column; gap: 0.15rem; }
.masthead-eyebrow {
  font-family: 'Open Sans', sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--maroon);
  font-weight: 600;
}
.masthead-title {
  font-family: 'Roboto Slab', serif !important;
  font-size: 2.1rem;
  font-weight: 700 !important;
  color: var(--ink);
  line-height: 1.1;
  margin: 0.15rem 0 0.1rem 0;
}
.masthead-sub {
  font-family: 'Roboto Slab', serif;
  font-style: italic;
  color: var(--muted);
  font-size: 0.95rem;
  font-weight: 300;
}
.masthead-right {
  text-align: right;
  font-family: 'JetBrains Mono', SFMono-Regular, monospace;
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.06em;
  line-height: 1.65;
}

.preview-strip {
  background: var(--paper);
  border-left: 3px solid var(--maroon);
  padding: 0.7rem 1rem;
  margin: 0.6rem 0 1.4rem 0;
  font-size: 0.88rem;
  color: var(--ink);
}
.preview-strip b {
  font-family: 'Roboto Slab', serif;
  color: var(--maroon);
  text-transform: uppercase;
  font-size: 0.74rem;
  letter-spacing: 0.18em;
  margin-right: 0.6rem;
}

/* KEY FIGURES STAT BAND -------------------------------------------------- */
.stat-band {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  margin: 1.3rem 0 0.6rem 0;
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
}
.stat {
  padding: 1.1rem 1.2rem;
  border-right: 1px solid var(--rule);
}
.stat:last-child { border-right: none; }
.stat-label {
  font-family: 'Open Sans', sans-serif;
  text-transform: uppercase;
  font-size: 0.66rem;
  letter-spacing: 0.18em;
  color: var(--muted);
  margin-bottom: 0.45rem;
}
.stat-value {
  font-family: 'Roboto Slab', serif;
  font-size: 1.95rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.05;
}
.stat-unit {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.3rem;
  letter-spacing: 0.04em;
}
.stat-value.warn { color: var(--maroon); }
.stat-value.ok   { color: var(--sage); }

/* SECTION RULE ----------------------------------------------------------- */
.section-rule {
  display: flex;
  align-items: baseline;
  gap: 0.7rem;
  border-bottom: 1px solid var(--rule);
  padding-bottom: 0.4rem;
  margin: 2.2rem 0 1rem 0;
}
.section-rule .num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--maroon);
  letter-spacing: 0.14em;
}
.section-rule .ttl {
  font-family: 'Roboto Slab', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ink);
}

/* TICKER ROWS ------------------------------------------------------------ */
.ticker-row {
  display: grid;
  grid-template-columns: 90px 1.3fr 0.7fr 0.7fr 1fr 0.7fr;
  gap: 0.7rem;
  align-items: center;
  padding: 0.9rem 0.4rem;
  border-bottom: 1px solid var(--rule);
}
.ticker-row.head {
  border-bottom: 1px solid var(--ink);
  padding-bottom: 0.55rem;
}
.ticker-row.head div {
  font-family: 'Open Sans', sans-serif;
  text-transform: uppercase;
  font-size: 0.66rem;
  letter-spacing: 0.18em;
  color: var(--muted);
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
  color: var(--ink);
}
.ticker-row .nm small {
  display: block;
  font-family: 'Open Sans', sans-serif;
  font-weight: 400;
  color: var(--muted);
  font-size: 0.78rem;
  margin-top: 0.15rem;
}
.ticker-row .num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.93rem;
  color: var(--ink);
  text-align: right;
}
.ticker-row .num small {
  font-family: 'Open Sans', sans-serif;
  font-size: 0.7rem;
  color: var(--muted);
}

.pill {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  font-family: 'Open Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #FFFFFF;
  border-radius: 1px;
  white-space: nowrap;
}
.dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  margin-right: 0.4rem;
  vertical-align: middle;
}

/* LENS SELECTOR (Streamlit radio override) ------------------------------- */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
  flex-direction: row !important;
  gap: 0 !important;
  margin: 0.6rem 0 0.4rem 0 !important;
  border-top: 1px solid var(--rule) !important;
  border-bottom: 1px solid var(--rule) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
  flex: 1 1 0 !important;
  margin: 0 !important;
  padding: 0.95rem 0.6rem !important;
  border-right: 1px solid var(--rule) !important;
  text-align: center !important;
  cursor: pointer !important;
  transition: all 0.18s ease-out !important;
  background: #FFFFFF !important;
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
  font-size: 0.98rem !important;
  color: var(--muted) !important;
  margin: 0 !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
  background: var(--paper-soft) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover p {
  color: var(--ink) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
  background: var(--navy) !important;
  border-bottom: 3px solid var(--maroon) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
  color: #FFFFFF !important;
  font-weight: 600 !important;
}

/* Footer ----------------------------------------------------------------- */
.footer-rule {
  margin-top: 3.5rem;
  padding-top: 1rem;
  border-top: 3px double var(--rule);
  font-size: 0.82rem;
  color: var(--muted);
  font-family: 'Open Sans', sans-serif;
  line-height: 1.6;
}

/* Streamlit chrome cleanup */
header[data-testid="stHeader"] { background: transparent !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.stDeployButton { display: none; }
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
    VOL. I · NO. 1<br>
    {today}<br>
    METHODOLOGY · CRREM v1.0 + NZIF
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
  <strong style="font-family:'Roboto Slab', serif; color:#1A2436;">Colophon.</strong>
  Methodology follows the CRREM Technical Blueprint v1.0
  (<a href="https://crrem.org/library/technical-blueprint" style="color:#385676;">crrem.org/library</a>)
  and the IIGCC Net Zero Investment Framework v2.0 (listed equity component + real estate annex).
  Each issuer is modelled as a mini-portfolio of pseudo-assets carved by disclosed geographic and
  use-type segmentation; the CRREM compute then runs at pseudo-asset level and aggregates
  GIA-weighted to issuer and portfolio. Four audience-specific lenses present the same underlying
  model. Inputs in this preview are illustrative placeholders. Built for
  Duff &amp; Phelps Investment Management as a methodology demonstration.
</div>
""",
    unsafe_allow_html=True,
)
