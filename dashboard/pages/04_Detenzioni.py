"""Detenzioni & Canoni — Chi usa i beni pubblici e a quali condizioni."""

import altair as alt
import plotly.express as px
import streamlit as st

from sources import (
    detenzioni_per_finalita,
    detenzioni_per_tipo,
    detenzioni_soggetti,
    fmt_eur,
    kpi_detenzioni,
)

st.title("💰 Detenzioni & Canoni")
st.markdown("564.000 detenzioni a favore di terzi per €1,97 miliardi di canoni.")

# ── KPI ──────────────────────────────────────────────────────────────────────

df_kpi = kpi_detenzioni()
if df_kpi is None or df_kpi.empty:
    st.warning("Nessun dato.")
    st.stop()

row = df_kpi.iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Detenzioni totali", f"{int(row['totale']):,}".replace(",", "."))
c2.metric("Con canone > 0", f"{int(row['con_canone']):,}".replace(",", "."))
c3.metric("Canoni totali", fmt_eur(row["totale_canoni"]))
c4.metric("Canone medio", fmt_eur(row["media_canone"]))

st.markdown("---")

# ── Tipo detenzione ──────────────────────────────────────────────────────────

st.subheader("📋 Per tipo di detenzione")

df_tipo = detenzioni_per_tipo()
if df_tipo is not None and not df_tipo.empty:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        chart = (
            alt.Chart(df_tipo)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#6366f1")
            .encode(
                x=alt.X("n:Q", title="N. detenzioni", axis=alt.Axis(format="~s")),
                y=alt.Y("tipo:N" if "tipo" in df_tipo.columns else "tipo_detenzione_terzi:N", title="", sort="-x"),
                tooltip=[alt.Tooltip("n:Q", format=",")],
            ).properties(height=250)
        )
        st.altair_chart(chart, width="stretch")
    with col_t2:
        col_canone = "canone_totale" if "canone_totale" in df_tipo.columns else "canone_totale"
        df_c = df_tipo[df_tipo[col_canone] > 0] if col_canone in df_tipo.columns else df_tipo
        if not df_c.empty:
            chart2 = (
                alt.Chart(df_c)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#22c55e")
                .encode(
                    x=alt.X(f"{col_canone}:Q", title="Canone totale (€)", axis=alt.Axis(format="~s")),
                    y=alt.Y("tipo:N" if "tipo" in df_c.columns else "tipo_detenzione_terzi:N", title="", sort="-x"),
                ).properties(height=250)
            )
            st.altair_chart(chart2, width="stretch")

st.markdown("---")

# ── Finalità ─────────────────────────────────────────────────────────────────

st.subheader("🎯 Finalità delle detenzioni")

df_fin = detenzioni_per_finalita()
if df_fin is not None and not df_fin.empty:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fig_fin = px.pie(df_fin, values="n", names="finalita", hole=0.4)
        fig_fin.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300,
                              showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                              paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_fin, width="stretch")
    with col_f2:
        df_fin_eur = df_fin[df_fin["canone_totale"] > 0]
        if not df_fin_eur.empty:
            fig_fin2 = px.pie(df_fin_eur, values="canone_totale", names="finalita", hole=0.4)
            fig_fin2.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300,
                                   showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                                   paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_fin2, width="stretch")

st.markdown("---")

# ── Soggetti ─────────────────────────────────────────────────────────────────

st.subheader("👥 Soggetti riceventi")

df_pa = detenzioni_soggetti()
if df_pa is not None and not df_pa.empty:
    fig_pa = px.pie(df_pa, values="n", names="tipo_pa", hole=0.4)
    fig_pa.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                         paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_pa, width="stretch")

st.caption("Dati: MEF — 2023 · CC BY 4.0")
