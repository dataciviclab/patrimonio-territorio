"""Mappa immobili — Pin singoli per immobile nel comune selezionato."""

import plotly.express as px
import streamlit as st

from sources import fmt_mq, immobili_comune, kpi_comune, mappa_comuni

st.title("🗺️ Mappa Immobili Pubblici")
st.markdown("Seleziona un comune per vedere i singoli immobili sulla mappa.")

# ── Elenco comuni per filtri cascata ─────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def elenco_comuni():
    df = mappa_comuni()
    return df[["comune_bene", "provincia_bene", "regione_bene"]].drop_duplicates().sort_values("comune_bene")

df_comuni = elenco_comuni()

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    regioni = sorted(df_comuni["regione_bene"].unique())
    regione = st.selectbox("Regione", regioni, index=regioni.index("LAZIO") if "LAZIO" in regioni else 0)
with col_f2:
    prov_list = sorted(df_comuni[df_comuni["regione_bene"] == regione]["provincia_bene"].unique())
    provincia = st.selectbox("Provincia", prov_list, index=prov_list.index("ROMA") if "ROMA" in prov_list else 0)
with col_f3:
    comuni_list = sorted(df_comuni[
        (df_comuni["regione_bene"] == regione) & (df_comuni["provincia_bene"] == provincia)
    ]["comune_bene"].unique())
    comune = st.selectbox("Comune", comuni_list, index=0)

# ── Filtri aggiuntivi ────────────────────────────────────────────────────────

col_f4, col_f5 = st.columns(2)
with col_f4:
    filtro_tipo = st.multiselect("Tipologia bene", [
        "Abitazione", "Terreno agricolo", "Terreno urbano",
        "Ufficio strutturato ed assimilabili", "Locale commerciale, negozio",
        "Edificio scolastico", "Palazzo storico, castello",
        "Magazzino e locali di deposito", "Impianto sportivo",
    ], default=[], key="f_tipo")
with col_f5:
    filtro_util = st.multiselect("Stato utilizzo", [
        "Utilizzato direttamente", "Non utilizzato", "Inutilizzabile",
        "In ristrutturazione/manutenzione",
    ], default=[], key="f_util")

# ── Query immobili del comune ────────────────────────────────────────────────

with st.spinner(f"Caricamento {comune}..."):
    df_imm = immobili_comune(
        comune, provincia, regione,
        tuple(filtro_tipo), tuple(filtro_util),
    )

if df_imm.empty:
    st.warning("Nessun immobile per i filtri selezionati.")
    st.stop()

# ── KPI del comune ───────────────────────────────────────────────────────────

kpi = kpi_comune(comune)
row = kpi.iloc[0]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Immobili totali", f"{int(row['totale']):,}".replace(",", "."))
c2.metric("Non utilizzati", f"{int(row['non_utilizzati']):,}".replace(",", "."),
          f"{100.0 * row['non_utilizzati'] / row['totale']:.1f}%", delta_color="inverse")
c3.metric("Inutilizzabili", f"{int(row['inutilizzabili']):,}".replace(",", "."))
c4.metric("Superficie", fmt_mq(row["superficie"]))
c5.metric("Vincolati", f"{int(row['vincolati']):,}".replace(",", "."))

st.markdown("---")

# ── Mappa pin singoli ────────────────────────────────────────────────────────

center_lat = df_imm["lat"].mean()
center_lon = df_imm["lon"].mean()

color_map = {
    "Utilizzato direttamente": "#22c55e",
    "Non utilizzato": "#ef4444",
    "Inutilizzabile": "#94a3b8",
    "In ristrutturazione/manutenzione": "#f59e0b",
}

fig = px.scatter_map(
    df_imm,
    lat="lat", lon="lon",
    color="utilizzo_bene",
    color_discrete_map=color_map,
    hover_name="indirizzo",
    hover_data={
        "tipologia_bene": True,
        "superficie_riferimento_mq": ":,.0f",
        "vincoli": True,
        "natura_giuridica_bene": True,
        "amministrazione_denominazione": True,
        "lat": ":.6f", "lon": ":.6f",
    },
    zoom=13 if len(df_imm) < 1000 else 11,
    center={"lat": center_lat, "lon": center_lon},
    map_style="carto-darkmatter",
)
fig.update_traces(marker=dict(size=8, opacity=0.9))
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=-0.1),
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, width="stretch")

st.markdown("---")

# ── Tabella immobili ─────────────────────────────────────────────────────────

st.subheader(f"📋 Immobili — {comune} ({len(df_imm)} risultati)")

df_table = df_imm[["indirizzo", "numero_civico", "tipologia_bene", "utilizzo_bene",
                     "vincoli", "superficie_riferimento_mq", "natura_giuridica_bene",
                     "amministrazione_denominazione", "epoca_costruzione"]].copy()
df_table.columns = ["Indirizzo", "Civico", "Tipo", "Utilizzo", "Vincoli",
                     "Superficie (mq)", "Natura giuridica", "Ente", "Epoca"]

st.dataframe(
    df_table,
    width="stretch",
    height=400,
    column_config={
        "Indirizzo": st.column_config.TextColumn(width="medium"),
        "Tipo": st.column_config.TextColumn(width="medium"),
        "Superficie (mq)": st.column_config.NumberColumn(format="%d"),
    },
)

st.caption(f"Dati: MEF — 2023 · {len(df_imm)} immobili a {comune} · CC BY 4.0")
