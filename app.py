"""CRREM Portfolio Assessment — Preview.

Single-page Streamlit demonstration in DPIM brand styling.

Run:
    streamlit run app.py

This is a methodology preview built for Duff & Phelps Investment Management.
Inputs are illustrative; replace with figures from the issuers' most recent
sustainability reports before any decision use.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from crrem_core import rollup_ticker, rollup_portfolio
from data import TICKERS, EF_ANCHORS, PATHWAY_ANCHORS
from nzif import classify, CATEGORY_COLOR, CATEGORIES, portfolio_distribution


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
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@300;400;500;600;700&family=Open+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
      :root {{
        --navy: {NAVY};
        --navy-deep: {NAVY_DEEP};
        --ink: {INK};
        --maroon: {MAROON};
        --ochre: {OCHRE};
        --sage: {SAGE};
        --rule: {RULE};
        --paper: {PAPER};
        --paper-soft: {PAPER_SOFT};
        --muted: {MUTED};
      }}
      html, body, [class*="css"] {{
        font-family: 'Open Sans', Helvetica, Arial, sans-serif;
        color: var(--ink);
        background: #FFFFFF;
      }}
      .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        max-width: 1280px;
      }}
      h1, h2, h3, h4, .display, .masthead-title {{
        font-family: 'Roboto Slab', Georgia, serif;
        color: var(--ink);
        font-weight: 600;
        letter-spacing: -0.01em;
      }}
      h1 {{ font-size: 2.1rem; line-height: 1.15; margin-bottom: 0.1rem; }}
      h2 {{ font-size: 1.35rem; margin-top: 2.4rem; margin-bottom: 0.6rem; }}
      h3 {{ font-size: 1.05rem; margin-top: 1.5rem; }}
      p, li {{ font-size: 0.96rem; line-height: 1.55; }}
      .mono, .figure {{ font-family: 'JetBrains Mono', SFMono-Regular, Menlo, monospace; }}

      /* MASTHEAD ---------------------------------------------------------- */
      .masthead {{
        border-top: 3px solid var(--navy);
        border-bottom: 1px solid var(--rule);
        padding: 1rem 0 0.7rem 0;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
      }}
      .masthead-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
      .masthead-eyebrow {{
        font-family: 'Open Sans', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--maroon);
        font-weight: 600;
      }}
      .masthead-title {{
        font-family: 'Roboto Slab', serif;
        font-size: 1.95rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.1;
      }}
      .masthead-sub {{
        font-family: 'Roboto Slab', serif;
        font-style: italic;
        color: var(--muted);
        font-size: 0.92rem;
        font-weight: 300;
        margin-top: 0.1rem;
      }}
      .masthead-right {{
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--muted);
        letter-spacing: 0.06em;
      }}

      .preview-strip {{
        background: var(--paper);
        border-left: 3px solid var(--maroon);
        padding: 0.65rem 1rem;
        margin: 0.8rem 0 1.6rem 0;
        font-size: 0.86rem;
        color: var(--ink);
      }}
      .preview-strip b {{
        font-family: 'Roboto Slab', serif;
        color: var(--maroon);
        text-transform: uppercase;
        font-size: 0.74rem;
        letter-spacing: 0.18em;
        margin-right: 0.6rem;
      }}

      /* KEY FIGURES STAT-BAND --------------------------------------------- */
      .stat-band {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        margin: 1.5rem 0 1.2rem 0;
        border-top: 1px solid var(--rule);
        border-bottom: 1px solid var(--rule);
      }}
      .stat {{
        padding: 1.1rem 1.2rem;
        border-right: 1px solid var(--rule);
      }}
      .stat:last-child {{ border-right: none; }}
      .stat-label {{
        font-family: 'Open Sans', sans-serif;
        text-transform: uppercase;
        font-size: 0.66rem;
        letter-spacing: 0.18em;
        color: var(--muted);
        margin-bottom: 0.4rem;
      }}
      .stat-value {{
        font-family: 'Roboto Slab', serif;
        font-size: 1.9rem;
        font-weight: 600;
        color: var(--ink);
        line-height: 1.05;
      }}
      .stat-unit {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--muted);
        margin-top: 0.25rem;
        letter-spacing: 0.04em;
      }}
      .stat-value.warn {{ color: var(--maroon); }}
      .stat-value.ok   {{ color: var(--sage); }}

      /* SECTION RULE ------------------------------------------------------ */
      .section-rule {{
        display: flex;
        align-items: baseline;
        gap: 0.7rem;
        border-bottom: 1px solid var(--rule);
        padding-bottom: 0.35rem;
        margin: 2.4rem 0 1rem 0;
      }}
      .section-rule .num {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--maroon);
        letter-spacing: 0.14em;
      }}
      .section-rule .ttl {{
        font-family: 'Roboto Slab', serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--ink);
        letter-spacing: -0.005em;
      }}

      /* TICKER ROWS ------------------------------------------------------- */
      .ticker-row {{
        display: grid;
        grid-template-columns: 90px 1.3fr 0.6fr 0.7fr 1fr 28px;
        gap: 0.7rem;
        align-items: center;
        padding: 0.85rem 0.4rem;
        border-bottom: 1px solid var(--rule);
      }}
      .ticker-row.head {{
        border-bottom: 1px solid var(--ink);
        padding-bottom: 0.5rem;
      }}
      .ticker-row.head div {{
        font-family: 'Open Sans', sans-serif;
        text-transform: uppercase;
        font-size: 0.66rem;
        letter-spacing: 0.18em;
        color: var(--muted);
      }}
      .ticker-row .sym {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: var(--navy);
        font-size: 0.95rem;
        letter-spacing: 0.04em;
      }}
      .ticker-row .nm {{
        font-family: 'Roboto Slab', serif;
        font-weight: 500;
        color: var(--ink);
      }}
      .ticker-row .nm small {{
        display: block;
        font-family: 'Open Sans', sans-serif;
        font-weight: 400;
        color: var(--muted);
        font-size: 0.78rem;
        margin-top: 0.1rem;
      }}
      .ticker-row .num {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.92rem;
        color: var(--ink);
        text-align: right;
      }}
      .ticker-row .num small {{
        font-family: 'Open Sans', sans-serif;
        font-size: 0.7rem;
        color: var(--muted);
      }}

      .pill {{
        display: inline-block;
        padding: 0.22rem 0.55rem;
        font-family: 'Open Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        color: #FFFFFF;
        border-radius: 1px;
        white-space: nowrap;
      }}

      .dot {{
        display: inline-block;
        width: 9px; height: 9px;
        border-radius: 50%;
        margin-right: 0.4rem;
        vertical-align: middle;
      }}

      .footer-rule {{
        margin-top: 3.5rem;
        padding-top: 1rem;
        border-top: 3px double var(--rule);
        font-size: 0.78rem;
        color: var(--muted);
        font-family: 'Open Sans', sans-serif;
      }}

      /* expander tweak */
      details summary {{
        font-family: 'Roboto Slab', serif !important;
        font-weight: 500;
      }}

      /* Streamlit chrome cleanup */
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
# Portfolio key figures
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
        <div class="stat-unit">kgCO₂e / m² · GIA-weighted · {ticker_results[0]['pseudo_assets'][0]['country'] and 2024}</div>
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
# Trajectory chart
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-rule"><div class="num">§ 01</div>'
    '<div class="ttl">Portfolio trajectory against the 1.5°C pathway</div></div>',
    unsafe_allow_html=True,
)

fig = go.Figure()
years = sorted(portfolio["trajectory"].keys())
fig.add_trace(go.Scatter(
    x=years, y=[portfolio["pathway"][y] for y in years],
    mode="lines", name="CRREM 1.5°C pathway",
    line=dict(color=NAVY, width=2.2, dash="dot"),
    hovertemplate="<b>%{x}</b> · Pathway %{y:.1f} kgCO₂e/m²<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=years, y=[portfolio["trajectory"][y] for y in years],
    mode="lines", name="Portfolio trajectory (flat demand)",
    line=dict(color=MAROON, width=2.6),
    hovertemplate="<b>%{x}</b> · Portfolio %{y:.1f} kgCO₂e/m²<extra></extra>",
))
if pf_mis != "Beyond 2050":
    fig.add_vline(
        x=int(pf_mis), line=dict(color=OCHRE, width=1.4, dash="dash"),
        annotation_text=f"  misalignment {pf_mis}",
        annotation_position="top right",
        annotation_font=dict(family="Roboto Slab", size=12, color=OCHRE),
    )
fig.update_layout(
    height=420,
    margin=dict(l=10, r=10, t=10, b=30),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Open Sans, sans-serif", color=INK, size=12),
    xaxis=dict(
        showgrid=False, showline=True, linecolor=RULE, ticks="outside",
        tickcolor=RULE, tickfont=dict(family="JetBrains Mono", size=11, color=MUTED),
    ),
    yaxis=dict(
        showgrid=True, gridcolor=RULE, gridwidth=0.5, zeroline=False,
        title=dict(text="kgCO₂e / m² · yr", font=dict(family="Roboto Slab", size=12, color=MUTED)),
        tickfont=dict(family="JetBrains Mono", size=11, color=MUTED),
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        font=dict(family="Open Sans", size=11, color=INK),
        bgcolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(font=dict(family="JetBrains Mono", size=12),
                    bgcolor=PAPER_SOFT, bordercolor=NAVY),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# NZIF distribution band
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-rule"><div class="num">§ 02</div>'
    '<div class="ttl">NZIF classification — distribution of portfolio by GIA</div></div>',
    unsafe_allow_html=True,
)

dist = portfolio["nzif_distribution"]
fig2 = go.Figure()
x_acc = 0.0
for cat in CATEGORIES:
    pct = dist.get(cat, 0.0)
    if pct <= 0:
        continue
    fig2.add_trace(go.Bar(
        x=[pct], y=[""], orientation="h",
        marker=dict(color=CATEGORY_COLOR[cat], line=dict(width=0)),
        name=cat, text=f"{cat} · {pct:.0f}%", textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="Open Sans", size=12, color="#FFFFFF"),
        hovertemplate=f"<b>{cat}</b><br>%{{x:.1f}}%% of GIA<extra></extra>",
    ))
    x_acc += pct
fig2.update_layout(
    barmode="stack",
    height=78,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    showlegend=False,
    xaxis=dict(visible=False, range=[0, 100]),
    yaxis=dict(visible=False),
)
st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

legend_html = "".join(
    f'<span style="margin-right:1.4rem; font-size:0.82rem; font-family:Open Sans;">'
    f'<span class="dot" style="background:{CATEGORY_COLOR[c]}"></span>{c}</span>'
    for c in CATEGORIES
)
st.markdown(f'<div style="margin-top:0.4rem;">{legend_html}</div>',
            unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Holdings table (custom HTML rows)
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-rule"><div class="num">§ 03</div>'
    '<div class="ttl">Holdings</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ticker-row head">
      <div>Ticker</div>
      <div>Issuer</div>
      <div style="text-align:right">Carbon int.</div>
      <div style="text-align:right">Misalignment</div>
      <div>NZIF classification</div>
      <div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

for t in ticker_results:
    ci = t["carbon_intensity_kgco2_m2"]
    mis = t["misalignment_year"]
    mis_label = "Beyond 2050" if mis == "Beyond 2050" else str(mis)
    cat = t["nzif_category"]
    cat_color = CATEGORY_COLOR[cat]
    st.markdown(
        f"""
        <div class="ticker-row">
          <div class="sym">{t['ticker']}</div>
          <div class="nm">{t['name']}<small>{t['exchange']} · {len(t['pseudo_assets'])} pseudo-asset(s) · {t['total_gia_m2']/1_000_000:.2f} M m²</small></div>
          <div class="num">{ci:.1f}<small> kgCO₂e/m²</small></div>
          <div class="num">{mis_label}</div>
          <div><span class="pill" style="background:{cat_color}">{cat}</span></div>
          <div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Per-ticker drill-down
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-rule"><div class="num">§ 04</div>'
    '<div class="ttl">Issuer drill-down</div></div>',
    unsafe_allow_html=True,
)

choice = st.selectbox(
    "Select a holding",
    options=[t["ticker"] for t in ticker_results],
    format_func=lambda x: next(t["name"] + f"  ({x})" for t in ticker_results if t["ticker"] == x),
    label_visibility="collapsed",
)
sel = next(t for t in ticker_results if t["ticker"] == choice)

c1, c2 = st.columns([1.4, 1])
with c1:
    fig3 = go.Figure()
    years = sorted(sel["trajectory"].keys())
    fig3.add_trace(go.Scatter(
        x=years, y=[sel["pathway"][y] for y in years],
        mode="lines", name="CRREM 1.5°C pathway (blended)",
        line=dict(color=NAVY, width=2.0, dash="dot"),
    ))
    fig3.add_trace(go.Scatter(
        x=years, y=[sel["trajectory"][y] for y in years],
        mode="lines", name=f"{sel['ticker']} trajectory",
        line=dict(color=MAROON, width=2.6),
    ))
    mis = sel["misalignment_year"]
    if mis != "Beyond 2050":
        fig3.add_vline(
            x=int(mis), line=dict(color=OCHRE, width=1.4, dash="dash"),
            annotation_text=f"  {mis}", annotation_position="top right",
            annotation_font=dict(family="Roboto Slab", size=11, color=OCHRE),
        )
    fig3.update_layout(
        height=320, margin=dict(l=10, r=10, t=10, b=20),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Open Sans", color=INK, size=11),
        xaxis=dict(showgrid=False, showline=True, linecolor=RULE,
                   tickfont=dict(family="JetBrains Mono", size=10, color=MUTED)),
        yaxis=dict(showgrid=True, gridcolor=RULE, gridwidth=0.5,
                   title=dict(text="kgCO₂e / m² · yr",
                              font=dict(family="Roboto Slab", size=11, color=MUTED)),
                   tickfont=dict(family="JetBrains Mono", size=10, color=MUTED)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    font=dict(family="Open Sans", size=10, color=INK)),
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with c2:
    st.markdown(
        f"""
        <div style="background:{PAPER}; border-left:3px solid {CATEGORY_COLOR[sel['nzif_category']]};
                    padding:1rem 1.1rem; margin-bottom:0.8rem;">
          <div style="font-family:'Open Sans'; text-transform:uppercase;
                      font-size:0.66rem; letter-spacing:0.18em; color:{MUTED};">
            NZIF · listed equity
          </div>
          <div style="font-family:'Roboto Slab'; font-size:1.35rem; font-weight:600;
                      color:{CATEGORY_COLOR[sel['nzif_category']]}; margin-top:0.25rem;">
            {sel['nzif_category']}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Reasoning**")
    for line in sel["nzif_reasoning"]:
        st.markdown(f"- {line}")

st.markdown("**Pseudo-asset breakdown**")
pa_df = pd.DataFrame([
    {
        "Sleeve": p["label"],
        "Country": p["country"],
        "Type": p["property_type"],
        "GIA (m²)": f"{p['gia_m2']:,.0f}",
        "EUI (kWh/m²)": f"{p['eui_kwh_m2']:,.1f}",
        "Carbon int. (kgCO₂e/m²)": f"{p['carbon_intensity_kgco2_m2']:,.1f}",
        "Misalignment": p["misalignment_year"],
    }
    for p in sel["pseudo_assets"]
])
st.dataframe(pa_df, hide_index=True, use_container_width=True)

st.markdown(
    f'<p style="font-family:Roboto Slab; font-style:italic; color:{MUTED}; '
    f'font-size:0.88rem; margin-top:0.6rem;">{sel["disclosure_notes"]}</p>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Footer / colophon
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="footer-rule">
      <strong style="font-family:'Roboto Slab'; color:{INK};">Colophon.</strong>
      Methodology follows the CRREM Technical Blueprint v1.0
      (<a href="https://crrem.org/library/technical-blueprint" style="color:{NAVY};">crrem.org/library</a>)
      and the IIGCC Net Zero Investment Framework (listed equity + real estate annex).
      Each issuer is modelled as a mini-portfolio of pseudo-assets carved by disclosed geographic and use-type
      segmentation; CRREM compute then runs at pseudo-asset level and aggregates GIA-weighted to issuer and
      portfolio. Inputs in this preview are illustrative placeholders; reference pathways and emission factors
      are approximations of the published CRREM datasets. Built for Duff &amp; Phelps Investment Management.
    </div>
    """,
    unsafe_allow_html=True,
)
