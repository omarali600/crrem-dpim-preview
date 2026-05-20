"""CRREM Portfolio Assessment — Preview.

Single-page Streamlit demonstration in DPIM brand styling.
Four audience-specific lenses over the same portfolio model.

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
# Page config + global CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CRREM Portfolio Assessment — DPIM preview",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

NAVY        = "#385676"
NAVY_DEEP   = "#243B5A"
INK         = "#1A2436"
MAROON      = "#800000"
OCHRE       = "#B08D57"
SAGE        = "#6B8E6B"
RULE        = "#C8CCD2"
PAPER       = "#F5F3EE"
PAPER_SOFT  = "#FBFAF6"
MUTED       = "#5C6473"

st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@300;400;500;600;700&family=Open+Sans:wght@300;400;500;600;700&family=Spectral:ital,wght@0,400;0,500;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
      :root {{
        --navy: {NAVY}; --navy-deep: {NAVY_DEEP};
        --ink: {INK}; --maroon: {MAROON};
        --ochre: {OCHRE}; --sage: {SAGE};
        --rule: {RULE}; --paper: {PAPER};
        --paper-soft: {PAPER_SOFT}; --muted: {MUTED};
      }}
      html, body, [class*="css"] {{
        font-family: 'Open Sans', Helvetica, Arial, sans-serif;
        color: var(--ink); background: #FFFFFF;
      }}
      .block-container {{
        padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1280px;
      }}
      h1, h2, h3, h4, .display, .masthead-title {{
        font-family: 'Roboto Slab', Georgia, serif;
        color: var(--ink); font-weight: 600; letter-spacing: -0.01em;
      }}
      h1 {{ font-size: 2.1rem; line-height: 1.15; }}
      h2 {{ font-size: 1.35rem; margin-top: 2.4rem; }}
      h3 {{ font-size: 1.05rem; margin-top: 1.5rem; }}
      p, li {{ font-size: 0.96rem; line-height: 1.55; }}

      .masthead {{
        border-top: 3px solid var(--navy);
        border-bottom: 1px solid var(--rule);
        padding: 1rem 0 0.7rem 0;
        margin-bottom: 0.5rem;
        display: flex; align-items: baseline; justify-content: space-between;
        gap: 1rem; flex-wrap: wrap;
      }}
      .masthead-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
      .masthead-eyebrow {{
        font-size: 0.72rem; letter-spacing: 0.22em;
        text-transform: uppercase; color: var(--maroon); font-weight: 600;
      }}
      .masthead-title {{
        font-family: 'Roboto Slab', serif;
        font-size: 1.95rem; font-weight: 700; color: var(--ink); line-height: 1.1;
      }}
      .masthead-sub {{
        font-family: 'Roboto Slab', serif; font-style: italic;
        color: var(--muted); font-size: 0.92rem; font-weight: 300; margin-top: 0.1rem;
      }}
      .masthead-right {{
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; color: var(--muted); letter-spacing: 0.06em;
      }}

      .preview-strip {{
        background: var(--paper); border-left: 3px solid var(--maroon);
        padding: 0.65rem 1rem; margin: 0.8rem 0 1.4rem 0;
        font-size: 0.86rem; color: var(--ink);
      }}
      .preview-strip b {{
        font-family: 'Roboto Slab', serif; color: var(--maroon);
        text-transform: uppercase; font-size: 0.74rem;
        letter-spacing: 0.18em; margin-right: 0.6rem;
      }}

      .stat-band {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 0;
        margin: 1.3rem 0 0.6rem 0;
        border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
      }}
      .stat {{ padding: 1.1rem 1.2rem; border-right: 1px solid var(--rule); }}
      .stat:last-child {{ border-right: none; }}
      .stat-label {{
        text-transform: uppercase; font-size: 0.66rem;
        letter-spacing: 0.18em; color: var(--muted); margin-bottom: 0.4rem;
      }}
      .stat-value {{
        font-family: 'Roboto Slab', serif; font-size: 1.9rem;
        font-weight: 600; color: var(--ink); line-height: 1.05;
      }}
      .stat-unit {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; color: var(--muted);
        margin-top: 0.25rem; letter-spacing: 0.04em;
      }}
      .stat-value.warn {{ color: var(--maroon); }}
      .stat-value.ok   {{ color: var(--sage); }}

      .section-rule {{
        display: flex; align-items: baseline; gap: 0.7rem;
        border-bottom: 1px solid var(--rule);
        padding-bottom: 0.35rem;
        margin: 2.4rem 0 1rem 0;
      }}
      .section-rule .num {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
        color: var(--maroon); letter-spacing: 0.14em;
      }}
      .section-rule .ttl {{
        font-family: 'Roboto Slab', serif; font-size: 1.05rem;
        font-weight: 600; color: var(--ink);
      }}

      .ticker-row {{
        display: grid;
        grid-template-columns: 90px 1.3fr 0.7fr 0.7fr 1fr 0.7fr;
        gap: 0.7rem; align-items: center;
        padding: 0.85rem 0.4rem; border-bottom: 1px solid var(--rule);
      }}
      .ticker-row.head {{ border-bottom: 1px solid var(--ink); padding-bottom: 0.5rem; }}
      .ticker-row.head div {{
        text-transform: uppercase; font-size: 0.66rem;
        letter-spacing: 0.18em; color: var(--muted);
      }}
      .ticker-row .sym {{
        font-family: 'JetBrains Mono', monospace; font-weight: 600;
        color: var(--navy); font-size: 0.95rem; letter-spacing: 0.04em;
      }}
      .ticker-row .nm {{ font-family: 'Roboto Slab', serif; font-weight: 500; color: var(--ink); }}
      .ticker-row .nm small {{
        display: block; font-family: 'Open Sans', sans-serif; font-weight: 400;
        color: var(--muted); font-size: 0.78rem; margin-top: 0.1rem;
      }}
      .ticker-row .num {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.92rem;
        color: var(--ink); text-align: right;
      }}
      .ticker-row .num small {{ font-family: 'Open Sans', sans-serif; font-size: 0.7rem; color: var(--muted); }}

      .pill {{
        display: inline-block; padding: 0.22rem 0.55rem;
        font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
        color: #FFFFFF; border-radius: 1px; white-space: nowrap;
      }}
      .dot {{
        display: inline-block; width: 9px; height: 9px;
        border-radius: 50%; margin-right: 0.4rem; vertical-align: middle;
      }}

      /* Lens selector ----------------------------------------------------- */
      .lens-bar {{
        display: flex; gap: 0; border-top: 1px solid var(--rule);
        border-bottom: 1px solid var(--rule);
        margin: 0.4rem 0 0.2rem 0;
      }}
      div[data-testid="stRadio"] > div {{
        flex-direction: row !important; gap: 0 !important;
        border-top: 1px solid var(--rule);
        border-bottom: 1px solid var(--rule);
        margin: 0.4rem 0 0.2rem 0;
      }}
      div[data-testid="stRadio"] label {{
        flex: 1 !important;
        padding: 0.95rem 0.6rem !important;
        border-right: 1px solid var(--rule) !important;
        background: #FFFFFF;
        font-family: 'Roboto Slab', serif !important;
        font-weight: 500 !important; font-size: 0.95rem !important;
        color: var(--muted) !important;
        cursor: pointer; text-align: center;
        transition: all 0.18s ease-out;
      }}
      div[data-testid="stRadio"] label:last-child {{ border-right: none !important; }}
      div[data-testid="stRadio"] label:hover {{
        background: var(--paper-soft); color: var(--ink) !important;
      }}
      div[data-testid="stRadio"] label[data-checked="true"] {{
        background: var(--navy) !important;
        color: #FFFFFF !important;
        border-bottom: 3px solid var(--maroon);
      }}
      div[data-testid="stRadio"] input {{ display: none !important; }}

      .footer-rule {{
        margin-top: 3.5rem; padding-top: 1rem;
        border-top: 3px double var(--rule);
        font-size: 0.78rem; color: var(--muted);
      }}

      header[data-testid="stHeader"] {{ background: transparent; }}
      footer {{ visibility: hidden; }}
      #MainMenu {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)


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
      Replace each ticker's energy and disclosure inputs with figures from the issuer's most recent sustainability report before any decision use.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Portfolio key figures (always visible)
# ---------------------------------------------------------------------------
pf_mis = portfolio["misalignment_year"]
pf_mis_str = "Beyond 2050" if pf_mis == "Beyond 2050" else str(pf_mis)
pf_mis_warn = pf_mis != "Beyond 2050" and int(pf_mis) <= 2035 if pf_mis != "Beyond 2050" else False
n_aligned_or_better = sum(
    1 for t in ticker_results
    if t["nzif_category"] in ("Achieving Net Zero", "Aligned", "Aligning")
)
aligned_share = sum(
    t["total_gia_m2"] for t in ticker_results
    if t["nzif_category"] in ("Achieving Net Zero", "Aligned", "Aligning")
) / max(portfolio["total_gia_m2"], 1) * 100

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
    f"""
    <div class="footer-rule">
      <strong style="font-family:'Roboto Slab'; color:{INK};">Colophon.</strong>
      Methodology follows the CRREM Technical Blueprint v1.0
      (<a href="https://crrem.org/library/technical-blueprint" style="color:{NAVY};">crrem.org/library</a>)
      and the IIGCC Net Zero Investment Framework v2.0 (listed equity component + real estate annex).
      Each issuer is modelled as a mini-portfolio of pseudo-assets carved by disclosed geographic and
      use-type segmentation; the CRREM compute then runs at pseudo-asset level and aggregates
      GIA-weighted to issuer and portfolio. Four audience-specific lenses present the same underlying
      model. Inputs in this preview are illustrative placeholders; reference pathways and emission
      factors are approximations of the published CRREM datasets. Built for Duff &amp; Phelps
      Investment Management as a methodology demonstration.
    </div>
    """,
    unsafe_allow_html=True,
)
