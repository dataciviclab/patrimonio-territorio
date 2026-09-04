"""Territorio — Ranking regioni e province."""

import plotly.express as px
import streamlit as st

from sources import regioni_inutilizzati

st.title("🏘️ Territorio")
st.markdown("Distribuzione geografica del patrimonio immobiliare pubblico per regione.")

# ── Mapping nomi regione → GEOJSON ──────────────────────────────────────────

REGION_MAP = {
    "ABRUZZO": "Abruzzo",
    "BASILICATA": "Basilicata",
    "CALABRIA": "Calabria",
    "CAMPANIA": "Campania",
    "EMILIA ROMAGNA": "Emilia-Romagna",
    "FRIULI VENEZIA GIULIA": "Friuli-Venezia Giulia",
    "LAZIO": "Lazio",
    "LIGURIA": "Liguria",
    "LOMBARDIA": "Lombardia",
    "MARCHE": "Marche",
    "MOLISE": "Molise",
    "PIEMONTE": "Piemonte",
    "PUGLIA": "Puglia",
    "SARDEGNA": "Sardegna",
    "SICILIA": "Sicilia",
    "TOSCANA": "Toscana",
    "TRENTINO ALTO ADIGE": "Trentino-Alto Adige/Südtirol",
    "UMBRIA": "Umbria",
    "VALLE D'AOSTA": "Valle d'Aosta/Vallée d'Aoste",
    "VENETO": "Veneto",
}

GEOJSON_URL = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"

# ── Carica dati ──────────────────────────────────────────────────────────────

df_reg = regioni_inutilizzati()
if df_reg is None or df_reg.empty:
    st.warning("Nessun dato.")
    st.stop()

# Aggiungi colonna con nome GEOJSON
df_reg["reg_name"] = df_reg["regione_bene"].map(REGION_MAP)

metrica = st.radio("Metrica", ["% Non utilizzati", "N. immobili"], horizontal=True)

metric_col_map = {
    "% Non utilizzati": "pct_inutilizzati",
    "N. immobili": "totale",
}
metric_col = metric_col_map[metrica]

# ── Choropleth ───────────────────────────────────────────────────────────────

fig = px.choropleth(
    df_reg, geojson=GEOJSON_URL, locations="reg_name",
    featureidkey="properties.reg_name", color=metric_col,
    color_continuous_scale="Reds" if "Non utilizzati" in metrica else "Blues",
    hover_name="regione_bene",
    hover_data={"reg_name": False, "totale": ":,", "non_utilizzati": ":,",
                "pct_inutilizzati": ":.1f", metric_col: False},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=500,
                  coloraxis_colorbar=dict(title=metrica), paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, width="stretch")

st.markdown("---")

# ── Ranking ──────────────────────────────────────────────────────────────────

st.subheader("📊 Ranking regioni")

df_sorted = df_reg.sort_values(metric_col, ascending=False)
display_df = df_sorted[["regione_bene", "totale", "non_utilizzati", "pct_inutilizzati"]].copy()
display_df.columns = ["Regione", "Totale", "Non utilizzati", "% Inutilizzati"]
st.dataframe(display_df.reset_index(drop=True), width="stretch", height=520,
             column_config={
                 "Regione": st.column_config.TextColumn(width="medium"),
                 "Totale": st.column_config.NumberColumn(format="%d"),
                 "Non utilizzati": st.column_config.NumberColumn(format="%d"),
                 "% Inutilizzati": st.column_config.NumberColumn(format="%.1f"),
             })

st.caption("Dati: MEF — 2023 · CC BY 4.0")
