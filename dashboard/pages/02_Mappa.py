"""Mappa immobili — Pin singoli per immobile nel comune selezionato."""

import duckdb
import plotly.express as px
import streamlit as st

from sources import IMMOBILI_CLEAN, fmt_mq

st.title("🗺️ Mappa Immobili Pubblici")
st.markdown("Seleziona un comune per vedere i singoli immobili sulla mappa.")

if not IMMOBILI_CLEAN.exists():
    st.warning("Dati non disponibili.")
    st.stop()

# ── Carica elenco comuni (leggero) ───────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def elenco_comuni():
    con = duckdb.connect()
    return con.sql(f"""
        SELECT DISTINCT comune_bene, provincia_bene, regione_bene,
            ROUND(AVG(latitudine), 5) AS lat,
            ROUND(AVG(longitudine), 5) AS lon
        FROM read_parquet('{IMMOBILI_CLEAN}')
        WHERE latitudine IS NOT NULL
        GROUP BY comune_bene, provincia_bene, regione_bene
        ORDER BY comune_bene
    """).df()

df_comuni = elenco_comuni()

# ── Filtri cascata ───────────────────────────────────────────────────────────

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
    comune = st.selectbox("Comune", comuni_list, index=comuni_list.index("ROMA") if "ROMA" in comuni_list else 0)

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

con = duckdb.connect()
where = [f"comune_bene = '{comune}'", "latitudine IS NOT NULL"]
if filtro_tipo:
    placeholders = ", ".join(f"'{t}'" for t in filtro_tipo)
    where.append(f"tipologia_bene IN ({placeholders})")
if filtro_util:
    placeholders = ", ".join(f"'{u}'" for u in filtro_util)
    where.append(f"utilizzo_bene IN ({placeholders})")

where_sql = " AND ".join(where)

df_imm = con.sql(f"""
    SELECT
        latitudine AS lat, longitudine AS lon,
        id_bene, tipologia_bene, utilizzo_bene, vincoli,
        natura_giuridica_bene, indirizzo, numero_civico,
        superficie_riferimento_mq, epoca_costruzione,
        amministrazione_denominazione
    FROM read_parquet('{IMMOBILI_CLEAN}')
    WHERE {where_sql}
""").df()

if df_imm.empty:
    st.warning("Nessun immobile per i filtri selezionati.")
    st.stop()

# ── KPI del comune ───────────────────────────────────────────────────────────

kpi = con.sql(f"""
    SELECT
        COUNT(*) AS totale,
        COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) AS non_utilizzati,
        COUNT(CASE WHEN utilizzo_bene = 'Inutilizzabile' THEN 1 END) AS inutilizzabili,
        ROUND(SUM(COALESCE(superficie_riferimento_mq, 0)), 0) AS superficie,
        COUNT(CASE WHEN vincoli != 'Nessuno' AND vincoli IS NOT NULL THEN 1 END) AS vincolati
    FROM read_parquet('{IMMOBILI_CLEAN}')
    WHERE comune_bene = '{comune}'
""").df()

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
