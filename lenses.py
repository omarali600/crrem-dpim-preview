"""Render functions for the four audience lenses.

Same portfolio model, four presentations:
  - Investment Committee
  - Regulatory / LP (NZIF + SFDR + TCFD + GRESB-comparable)
  - Engagement (per-issuer climate dossiers)
  - Analyst (raw working surface with disclosure provenance)
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nzif import CATEGORIES, CATEGORY_COLOR, portfolio_distribution


# Brand palette ------------------------------------------------------------
NAVY = "#385676"
NAVY_DEEP = "#243B5A"
INK = "#1A2436"
MAROON = "#800000"
OCHRE = "#B08D57"
SAGE = "#6B8E6B"
RULE = "#C8CCD2"
PAPER = "#F5F3EE"
PAPER_SOFT = "#FBFAF6"
MUTED = "#5C6473"


# Shared chart helpers -----------------------------------------------------
def _trajectory_chart(traj, pathway, misalignment_year, *,
                      height=380, title=None, traj_label="Portfolio trajectory"):
    fig = go.Figure()
    years = sorted(traj.keys())
    fig.add_trace(go.Scatter(
        x=years, y=[pathway[y] for y in years],
        mode="lines", name="CRREM 1.5°C pathway",
        line=dict(color=NAVY, width=2.2, dash="dot"),
        hovertemplate="<b>%{x}</b> · Pathway %{y:.1f} kgCO₂e/m²<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=years, y=[traj[y] for y in years],
        mode="lines", name=traj_label,
        line=dict(color=MAROON, width=2.6),
        hovertemplate=f"<b>%{{x}}</b> · {traj_label} %{{y:.1f}} kgCO₂e/m²<extra></extra>",
    ))
    if misalignment_year != "Beyond 2050":
        fig.add_vline(
            x=int(misalignment_year),
            line=dict(color=OCHRE, width=1.4, dash="dash"),
            annotation_text=f"  {misalignment_year}",
            annotation_position="top right",
            annotation_font=dict(family="Roboto Slab", size=11, color=OCHRE),
        )
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=20),
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
        hoverlabel=dict(font=dict(family="JetBrains Mono", size=12),
                        bgcolor=PAPER_SOFT, bordercolor=NAVY),
    )
    return fig


def _section(num: str, title: str):
    st.markdown(
        f'<div class="section-rule"><div class="num">§ {num}</div>'
        f'<div class="ttl">{title}</div></div>',
        unsafe_allow_html=True,
    )


# =========================================================================
# 1. Investment Committee
# =========================================================================
def render_ic(ticker_results, portfolio):
    _section("01", "Portfolio trajectory against the 1.5°C pathway")
    fig = _trajectory_chart(portfolio["trajectory"], portfolio["pathway"],
                            portfolio["misalignment_year"], height=420)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    _section("02", "NZIF classification — distribution of portfolio by GIA")
    _render_nzif_distribution(portfolio["nzif_distribution"])

    _section("03", "Holdings")
    _render_holdings_table(ticker_results, action_chip=True)

    _section("04", "Issuer drill-down")
    _render_drilldown(ticker_results)


def _render_nzif_distribution(dist):
    fig = go.Figure()
    for cat in CATEGORIES:
        pct = dist.get(cat, 0.0)
        if pct <= 0:
            continue
        fig.add_trace(go.Bar(
            x=[pct], y=[""], orientation="h",
            marker=dict(color=CATEGORY_COLOR[cat], line=dict(width=0)),
            name=cat, text=f"{cat} · {pct:.0f}%", textposition="inside",
            insidetextanchor="middle",
            textfont=dict(family="Open Sans", size=12, color="#FFFFFF"),
            hovertemplate=f"<b>{cat}</b><br>%{{x:.1f}}%% of GIA<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack", height=78,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        showlegend=False,
        xaxis=dict(visible=False, range=[0, 100]), yaxis=dict(visible=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    legend_html = "".join(
        f'<span style="margin-right:1.4rem; font-size:0.82rem; font-family:Open Sans;">'
        f'<span class="dot" style="background:{CATEGORY_COLOR[c]}"></span>{c}</span>'
        for c in CATEGORIES
    )
    st.markdown(f'<div style="margin-top:0.4rem;">{legend_html}</div>',
                unsafe_allow_html=True)


def _action_for(misalignment_year, nzif_category):
    if nzif_category == "Achieving Net Zero":
        return ("HOLD", SAGE)
    if nzif_category == "Aligned":
        return ("HOLD", SAGE)
    if nzif_category == "Aligning":
        return ("MONITOR", OCHRE)
    if nzif_category == "Committed to Aligning":
        return ("ENGAGE", OCHRE)
    return ("UNDERWEIGHT", MAROON)


def _render_holdings_table(ticker_results, action_chip=False):
    st.markdown(
        f"""
        <div class="ticker-row head">
          <div>Ticker</div>
          <div>Issuer</div>
          <div style="text-align:right">Carbon int.</div>
          <div style="text-align:right">Misalignment</div>
          <div>NZIF classification</div>
          <div>{'Action' if action_chip else ''}</div>
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
        action_html = ""
        if action_chip:
            label, color = _action_for(mis, cat)
            action_html = (
                f'<span class="pill" style="background:{color}; '
                f'font-size:0.68rem; letter-spacing:0.08em;">{label}</span>'
            )
        st.markdown(
            f"""
            <div class="ticker-row">
              <div class="sym">{t['ticker']}</div>
              <div class="nm">{t['name']}<small>{t['exchange']} · {len(t['pseudo_assets'])} pseudo-asset(s) · {t['total_gia_m2']/1_000_000:.2f} M m²</small></div>
              <div class="num">{ci:.1f}<small> kgCO₂e/m²</small></div>
              <div class="num">{mis_label}</div>
              <div><span class="pill" style="background:{cat_color}">{cat}</span></div>
              <div>{action_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_drilldown(ticker_results):
    choice = st.selectbox(
        "Select a holding",
        options=[t["ticker"] for t in ticker_results],
        format_func=lambda x: next(t["name"] + f"  ({x})"
                                   for t in ticker_results if t["ticker"] == x),
        label_visibility="collapsed",
    )
    sel = next(t for t in ticker_results if t["ticker"] == choice)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = _trajectory_chart(sel["trajectory"], sel["pathway"],
                                sel["misalignment_year"], height=320,
                                traj_label=f"{sel['ticker']} trajectory")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
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


# =========================================================================
# 2. Regulatory / LP
# =========================================================================
def _fossil_share(t):
    """Share of pseudo-asset energy from fossil sources (gas + oil + other fuels)."""
    total = 0.0; fossil = 0.0
    for pa in t["pseudo_assets"]:
        # we don't have raw carrier breakdown post-rollup, recover via ticker_results
        # this is a coarse signal for SFDR PAI 18 illustration only
        total += 1
        fossil += 1 if pa.get("country") in ("DE", "UK", "US") else 0.5
    return fossil / total if total else 0


def render_regulatory(ticker_results, portfolio, ticker_inputs):
    _section("01", "NZIF — Net Zero Investment Framework classification")
    _render_nzif_distribution(portfolio["nzif_distribution"])
    st.markdown(
        f"""
        <p style="color:{MUTED}; font-size:0.88rem; margin-top:0.9rem;">
        Classification derived per IIGCC NZIF v2.0, listed equity component, combined with the NZIF
        real-estate annex (CRREM-aligned). Methodology pinned at build time; the pinned NZIF
        version travels with each LP-facing export so any artifact is reproducible against a
        specific release.
        </p>
        """, unsafe_allow_html=True,
    )

    _section("02", "SFDR Principal Adverse Impact — indicator 18")
    st.markdown(
        '<p style="font-family:Roboto Slab; font-style:italic; color:#5C6473; font-size:0.9rem;">'
        '"Exposure to fossil fuels through real estate assets" — share of investments in real-estate '
        'assets involved in the extraction, storage, transport or manufacture of fossil fuels.'
        '</p>',
        unsafe_allow_html=True,
    )
    rows = []
    for t, raw in zip(ticker_results, ticker_inputs):
        gas_oil_share = 0.0
        for pa, src in zip(t["pseudo_assets"], raw.pseudo_assets):
            total = sum(src.energy_kwh.values())
            fossil = (src.energy_kwh.get("Gas", 0)
                      + src.energy_kwh.get("Oil", 0)
                      + src.energy_kwh.get("Other_Fuels", 0))
            gas_oil_share += (fossil / total if total else 0) * (pa["gia_m2"] / t["total_gia_m2"])
        rows.append({
            "Ticker": t["ticker"],
            "Issuer": t["name"],
            "GIA share (%)": f"{t['total_gia_m2'] / portfolio['total_gia_m2'] * 100:.1f}",
            "Fossil energy share (%)": f"{gas_oil_share * 100:.1f}",
            "Direct fossil-fuel involvement": "No (real estate use only)",
        })
    rows.append({
        "Ticker": "TOTAL",
        "Issuer": "Portfolio — GIA-weighted",
        "GIA share (%)": "100.0",
        "Fossil energy share (%)": f"{sum(float(r['Fossil energy share (%)']) * float(r['GIA share (%)']) / 100 for r in rows[:-1]):.1f}",
        "Direct fossil-fuel involvement": "—",
    })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption("Illustrative — replace with figures from the latest sustainability reports before LP reporting.")

    _section("03", "TCFD — scenario alignment narrative")
    pf_mis = portfolio["misalignment_year"]
    pf_mis_str = "beyond 2050" if pf_mis == "Beyond 2050" else f"in {pf_mis}"
    pf_ci = portfolio["carbon_intensity_kgco2_m2"]
    pf_pathway_now = portfolio["pathway"][2024]
    delta_pct = (pf_ci - pf_pathway_now) / pf_pathway_now * 100
    direction = "above" if delta_pct > 0 else "below"
    n_aligned = sum(1 for t in ticker_results
                    if t["nzif_category"] in ("Achieving Net Zero", "Aligned", "Aligning"))
    n_total = len(ticker_results)
    st.markdown(
        f"""
        <div style="background:{PAPER}; padding:1.2rem 1.4rem; border-left:3px solid {NAVY};
                    font-family:Spectral, Georgia, serif; font-size:1.0rem; line-height:1.65; color:{INK};">
        <strong>1.5°C scenario alignment (CRREM Global Pathways v3, illustrative).</strong>
        The portfolio's GIA-weighted carbon intensity for the reporting year is {pf_ci:.1f} kgCO₂e/m², which
        is {abs(delta_pct):.0f}% {direction} the 1.5°C pathway value of {pf_pathway_now:.1f} kgCO₂e/m² at the
        same date. Under a flat-demand projection with declining grid emission factors, the portfolio's
        trajectory crosses the 1.5°C pathway {pf_mis_str}. {n_aligned} of {n_total} holdings are classified
        as <em>Aligning</em> or better under the NZIF framework.
        <br><br>
        <strong>Drivers.</strong> Misalignment is concentrated in heat-dominated sleeves with high fossil
        carrier exposure (gas, oil, district heating from non-decarbonised networks). The portfolio's
        logistics sleeves remain well below pathway across all scenarios examined.
        <br><br>
        <strong>Action.</strong> Engagement is the primary lever for holdings currently classified
        <em>Committed to Aligning</em> or <em>Not Aligned</em>; underweight/exit considered for holdings
        whose disclosed decarbonisation roadmap does not credibly close the gap to 2030 pathway values.
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section("04", "Disclosure quality & climate governance — GRESB-comparable view")
    gov_rows = []
    for t, raw in zip(ticker_results, ticker_inputs):
        inputs = raw.nzif_inputs
        score = sum(1 for k in ("net_zero_commitment", "sbti_validated",
                                "short_term_target", "medium_term_target",
                                "decarbonization_capex_plan", "board_climate_oversight",
                                "remuneration_link") if inputs.get(k))
        gov_rows.append({
            "Ticker": t["ticker"],
            "Net-zero commitment": "✓" if inputs.get("net_zero_commitment") else "—",
            "SBTi validated": "✓" if inputs.get("sbti_validated") else "—",
            "Short-term target": "✓" if inputs.get("short_term_target") else "—",
            "Medium-term target": "✓" if inputs.get("medium_term_target") else "—",
            "Decarb. capex plan": "✓" if inputs.get("decarbonization_capex_plan") else "—",
            "Board oversight": "✓" if inputs.get("board_climate_oversight") else "—",
            "Remuneration link": "✓" if inputs.get("remuneration_link") else "—",
            "Disclosure quality": str(inputs.get("disclosure_quality", "")).title(),
            "Composite (of 7)": score,
        })
    st.dataframe(pd.DataFrame(gov_rows), hide_index=True, use_container_width=True)


# =========================================================================
# 3. Engagement
# =========================================================================
def _engagement_asks(t, raw):
    mis = t["misalignment_year"]
    asks = []
    if mis != "Beyond 2050" and int(mis) <= 2030:
        worst = max(t["pseudo_assets"], key=lambda p: p["carbon_intensity_kgco2_m2"])
        asks.append(("priority", "HIGH"))
        asks.append(("ask", f"Misalignment in {mis} driven by the {worst['label']} sleeve "
                            f"({worst['carbon_intensity_kgco2_m2']:.0f} kgCO₂e/m²). Request a "
                            f"sleeve-level decarbonisation roadmap with annual milestones."))
    elif mis != "Beyond 2050" and int(mis) <= 2040:
        asks.append(("priority", "MEDIUM"))
        asks.append(("ask", f"Pathway crossing forecast in {mis}. Request capex breakdown and "
                            f"interim 2028 / 2032 milestones."))
    else:
        asks.append(("priority", "LOW"))
        asks.append(("ask", "Steward trajectory. Confirm continued capex on the lower-intensity sleeves."))
    if not raw.nzif_inputs.get("sbti_validated"):
        asks.append(("ask", "Short-term target is not SBTi-validated. Ask for the validation timeline."))
    if not raw.nzif_inputs.get("remuneration_link"):
        asks.append(("ask", "Executive remuneration is not linked to net-zero milestones. "
                            "Recommend linkage at the next remuneration committee."))
    if raw.nzif_inputs.get("disclosure_quality") in ("medium", "low"):
        asks.append(("ask", "Disclosure quality is below high. Request Scope 1+2 disclosure "
                            "broken down by country and use-type segment in the next reporting cycle."))
    return asks


def render_engagement(ticker_results, ticker_inputs):
    _section("01", "Engagement priority ranking")
    ranked = sorted(
        zip(ticker_results, ticker_inputs),
        key=lambda x: (0 if x[0]["misalignment_year"] != "Beyond 2050"
                       else 9999, x[0]["misalignment_year"] if x[0]["misalignment_year"] != "Beyond 2050" else 9999)
    )
    for t, raw in ranked:
        asks = _engagement_asks(t, raw)
        priority = next((v for k, v in asks if k == "priority"), "LOW")
        ask_lines = [v for k, v in asks if k == "ask"]
        color = {"HIGH": MAROON, "MEDIUM": OCHRE, "LOW": SAGE}[priority]
        st.markdown(
            f"""
            <div style="border-left:3px solid {color}; background:{PAPER_SOFT};
                        padding:1.1rem 1.3rem; margin-bottom:1rem;">
              <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <div>
                  <div style="font-family:'JetBrains Mono'; color:{NAVY}; font-weight:600;
                              font-size:0.95rem; letter-spacing:0.04em;">{t['ticker']}</div>
                  <div style="font-family:'Roboto Slab'; font-size:1.18rem; font-weight:600;
                              color:{INK}; margin-top:0.1rem;">{t['name']}</div>
                </div>
                <div style="text-align:right;">
                  <span class="pill" style="background:{color}; font-size:0.7rem; letter-spacing:0.1em;">
                    {priority} PRIORITY
                  </span>
                  <div style="font-family:'JetBrains Mono'; font-size:0.78rem; color:{MUTED}; margin-top:0.3rem;">
                    Misalignment: {t['misalignment_year']}<br>
                    NZIF: {t['nzif_category']}
                  </div>
                </div>
              </div>
              <ul style="margin-top:0.9rem; padding-left:1.1rem;">
                {''.join(f'<li style="margin-bottom:0.35rem; font-size:0.93rem; line-height:1.5;">{a}</li>' for a in ask_lines)}
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _section("02", "Dossier export")
    st.markdown(
        '<p style="font-family:Open Sans; font-size:0.9rem; color:#5C6473;">'
        'In the production system, each ranked dossier is exportable as a PDF brief tied to the issuer\'s '
        'next AGM date, with verbatim quotes from the source sustainability report attached as evidence. '
        'The preview demonstrates the dossier content; the export pipeline is part of phase 2.'
        '</p>',
        unsafe_allow_html=True,
    )


# =========================================================================
# 4. Analyst
# =========================================================================
def render_analyst(ticker_results, ticker_inputs):
    _section("01", "Working surface")
    choice = st.selectbox(
        "Select a holding",
        options=[t["ticker"] for t in ticker_results],
        format_func=lambda x: next(t["name"] + f"  ({x})"
                                   for t in ticker_results if t["ticker"] == x),
        label_visibility="collapsed",
        key="analyst_choice",
    )
    sel = next(t for t in ticker_results if t["ticker"] == choice)
    sel_raw = next(r for r in ticker_inputs if r.ticker == choice)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = _trajectory_chart(sel["trajectory"], sel["pathway"],
                                sel["misalignment_year"], height=320,
                                traj_label=f"{sel['ticker']} trajectory")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c2:
        years_of_interest = [2024, 2030, 2040, 2050]
        rows = []
        for y in years_of_interest:
            rows.append({
                "Year": y,
                "Trajectory": f"{sel['trajectory'][y]:.1f}",
                "Pathway": f"{sel['pathway'][y]:.1f}",
                "Δ": f"{sel['trajectory'][y] - sel['pathway'][y]:+.1f}",
            })
        st.markdown("**Trajectory vs pathway · key years**")
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    _section("02", "Pseudo-asset disclosure record")
    for pa_result, pa_input in zip(sel["pseudo_assets"], sel_raw.pseudo_assets):
        st.markdown(
            f"""
            <div style="background:{PAPER_SOFT}; padding:1rem 1.2rem; margin-bottom:0.8rem;
                        border-left:2px solid {NAVY};">
              <div style="font-family:'Roboto Slab'; font-weight:600; font-size:1.05rem;
                          color:{INK}; margin-bottom:0.5rem;">
                {pa_result['label']}
                <span style="font-family:'JetBrains Mono'; font-size:0.75rem;
                             color:{MUTED}; font-weight:400; margin-left:0.6rem;">
                  {pa_result['country']} · {pa_result['property_type']}
                </span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        energy_df = pd.DataFrame([
            {
                "Carrier": carrier,
                "Consumption (kWh/yr)": f"{pa_input.energy_kwh.get(carrier, 0):,.0f}",
                "% of total": f"{(pa_input.energy_kwh.get(carrier, 0) / max(sum(pa_input.energy_kwh.values()), 1)) * 100:,.1f}%",
                "Source": "Issuer sustainability report (illustrative)",
                "Confidence": "high" if carrier == "Elec_Grid" else "medium",
            }
            for carrier in ("Elec_Grid", "Gas", "Oil", "District_Heating",
                            "District_Cooling", "Biomass", "Other_Fuels", "Renew_Consumed")
            if pa_input.energy_kwh.get(carrier, 0) > 0
        ])
        st.dataframe(energy_df, hide_index=True, use_container_width=True)

    _section("03", "Override layer (preview — read-only)")
    st.markdown(
        f"""
        <p style="font-family:Open Sans; font-size:0.9rem; color:{MUTED};">
        In the production system, every field on this page is overrideable inline. Overrides carry an
        author, timestamp, free-text reason, and become the value of record for compute — with the
        original disclosure still visible. Each override is written to the append-only audit log and
        appears in the regulatory export footnote chain.
        </p>
        <div style="background:{PAPER}; padding:0.9rem 1.1rem; border:1px dashed {RULE};
                    font-family:'JetBrains Mono'; font-size:0.82rem; color:{MUTED};">
          override.Elec_Grid = 64_800_000 kWh/yr
          &nbsp;&nbsp;reason: "issuer republished 2024 number after audit (note p.86 of restated report)"
          &nbsp;&nbsp;by: a.palmer@dpim · 2026-05-19T14:22:11Z
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section("04", "Audit trail (preview)")
    st.markdown(
        f"""
        <table style="width:100%; border-collapse:collapse; font-family:'JetBrains Mono';
                      font-size:0.82rem; color:{INK};">
          <thead>
            <tr style="border-bottom:1px solid {INK};">
              <th style="text-align:left; padding:0.5rem 0.4rem; font-family:'Open Sans';
                         font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase;
                         color:{MUTED}; font-weight:600;">Timestamp</th>
              <th style="text-align:left; padding:0.5rem 0.4rem; font-family:'Open Sans';
                         font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase;
                         color:{MUTED}; font-weight:600;">Actor</th>
              <th style="text-align:left; padding:0.5rem 0.4rem; font-family:'Open Sans';
                         font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase;
                         color:{MUTED}; font-weight:600;">Action</th>
              <th style="text-align:left; padding:0.5rem 0.4rem; font-family:'Open Sans';
                         font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase;
                         color:{MUTED}; font-weight:600;">Target</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid {RULE};">
              <td style="padding:0.45rem 0.4rem;">2026-05-19 14:22</td>
              <td style="padding:0.45rem 0.4rem; color:{NAVY};">a.palmer@dpim</td>
              <td style="padding:0.45rem 0.4rem;">override.create</td>
              <td style="padding:0.45rem 0.4rem;">{sel['ticker']} · Elec_Grid</td>
            </tr>
            <tr style="border-bottom:1px solid {RULE};">
              <td style="padding:0.45rem 0.4rem;">2026-05-19 09:11</td>
              <td style="padding:0.45rem 0.4rem; color:{NAVY};">system</td>
              <td style="padding:0.45rem 0.4rem;">harvest.run</td>
              <td style="padding:0.45rem 0.4rem;">{sel['ticker']} · issuer_sustainability_report</td>
            </tr>
            <tr style="border-bottom:1px solid {RULE};">
              <td style="padding:0.45rem 0.4rem;">2026-05-18 17:03</td>
              <td style="padding:0.45rem 0.4rem; color:{NAVY};">o.ali@dpim</td>
              <td style="padding:0.45rem 0.4rem;">export.pdf</td>
              <td style="padding:0.45rem 0.4rem;">portfolio · regulatory_lens · IC pack Q1 2026</td>
            </tr>
          </tbody>
        </table>
        <p style="font-family:Open Sans; font-size:0.84rem; color:{MUTED}; margin-top:0.7rem;">
        Audit log is append-only and hash-chained in the production system. Every export, override,
        harvest, and authentication event is captured. The preview shows representative entries.
        </p>
        """,
        unsafe_allow_html=True,
    )
