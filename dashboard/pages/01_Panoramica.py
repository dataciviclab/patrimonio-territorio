"""Panoramica — KPI nazionali e distribuzione beni."""

import altair as alt
import plotly.express as px
import streamlit as st

from sources import (
    distribuzione_tipologia,
    distribuzione_utilizzo,
    fmt_eur,
    fmt_mq,
    fmt_num,
    kpi_detenzioni,
    kpi_immobili,
    regioni_inutilizzati,
)

st.title("🏛️ Patrimonio Pubblico Italia")
st.markdown(
    "Il censimento immobiliare delle PA italiane: **3,25 milioni di beni**, "
    "100% georeferenziati. Quanto è utilizzato, quanto è abbandonato?"
)

# ── KPI ──────────────────────────────────────────────────────────────────────

df_kpi = kpi_immobili()
df_det = kpi_detenzioni()

if df_kpi is None or df_kpi.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

row = df_kpi.iloc[0]
totale = int(row["totale"])
non_util = int(row["non_utilizzati"])
util = int(row["utilizzati"])
sup_tot = float(row["superficie_totale"])

det_n = int(df_det.iloc[0]["totale"]) if df_det is not None and not df_det.empty else 0
det_canoni = float(df_det.iloc[0]["totale_canoni"]) if df_det is not None and not df_det.empty else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Immobili totali", fmt_num(totale))
c2.metric("Non utilizzati", fmt_num(non_util), f"{100.0 * non_util / totale:.1f}%", delta_color="inverse")
c3.metric("Detenzioni attive", fmt_num(det_n))
c4.metric("Canoni incassati", fmt_eur(det_canoni))
c5.metric("Superficie totale", fmt_mq(sup_tot))

st.markdown("---")

# ── Distribuzione utilizzo ───────────────────────────────────────────────────

st.subheader("📊 Stato di utilizzo dei beni")

df_util = distribuzione_utilizzo()
if df_util is not None and not df_util.empty:
    color_map = {
        "Utilizzato direttamente": "#22c55e",
        "Non utilizzato": "#ef4444",
        "Inutilizzabile": "#94a3b8",
        "In ristrutturazione/manutenzione": "#f59e0b",
        "Non specificato": "#6366f1",
    }
    col_chart, col_pie = st.columns([2, 1])
    with col_pie:
        fig_pie = px.pie(df_util, values="n", names="stato", color="stato",
                         color_discrete_map=color_map, hole=0.4)
        fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300,
                              showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                              paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, width="stretch")
    with col_chart:
        chart = (
            alt.Chart(df_util)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("n:Q", title="Numero beni", axis=alt.Axis(format="~s")),
                y=alt.Y("stato:N", title="", sort="-x"),
                color=alt.Color("stato:N", scale=alt.Scale(domain=list(color_map.keys()),
                                 range=list(color_map.values())), legend=None),
                tooltip=[alt.Tooltip("stato:N"), alt.Tooltip("n:Q", format=",")],
            ).properties(height=250)
        )
        st.altair_chart(chart, width="stretch")

st.markdown("---")

# ── Tipologia bene ───────────────────────────────────────────────────────────

st.subheader("🏗️ Tipologia di bene")

df_tipo = distribuzione_tipologia()
if df_tipo is not None and not df_tipo.empty:
    chart_tipo = (
        alt.Chart(df_tipo)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#6366f1")
        .encode(
            x=alt.X("n:Q", title="Numero beni", axis=alt.Axis(format="~s")),
            y=alt.Y("tipologia_bene:N", title="", sort="-x"),
            tooltip=[alt.Tooltip("tipologia_bene:N"), alt.Tooltip("n:Q", format=",")],
        ).properties(height=350)
    )
    st.altair_chart(chart_tipo, width="stretch")

st.markdown("---")

# ── Top regioni ──────────────────────────────────────────────────────────────

st.subheader("🗺️ Regioni per % immobili non utilizzati")

df_reg = regioni_inutilizzati()
if df_reg is not None and not df_reg.empty:
    df_reg = df_reg.sort_values("pct_inutilizzati", ascending=True)
    fig_reg = px.bar(df_reg, x="pct_inutilizzati", y="regione_bene", orientation="h",
                     color="pct_inutilizzati", color_continuous_scale="Reds",
                     labels={"pct_inutilizzati": "% Non utilizzati", "regione_bene": ""})
    fig_reg.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=500,
                          coloraxis_colorbar=dict(title="%"),
                          paper_bgcolor="rgba(0,0,0,0)")
    fig_reg.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_reg, width="stretch")

st.caption("Dati: MEF Dipartimento Economia — 2023 · CC BY 4.0")
