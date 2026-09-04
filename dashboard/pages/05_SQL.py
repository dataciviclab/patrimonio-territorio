"""Query SQL — Interroga direttamente i dati."""

import duckdb
import streamlit as st

from sources import IMMOBILI_CLEAN, DETENZIONI_CLEAN, ENTI_CLEAN

st.title("🧪 Query SQL")
st.markdown("Interroga direttamente i dati con DuckDB. I dataset sono disponibili come tabelle.")

# ── Dataset disponibili ──────────────────────────────────────────────────────

datasets = {
    "mef_patrimonio_immobili": IMMOBILI_CLEAN,
    "mef_patrimonio_detenzioni": DETENZIONI_CLEAN,
    "mef_patrimonio_enti": ENTI_CLEAN,
}

col1, col2 = st.columns([1, 3])
with col1:
    dataset = st.selectbox("Dataset", list(datasets.keys()))
with col2:
    sql = st.text_area("SQL", f"SELECT * FROM {dataset} LIMIT 10", height=100)

if st.button("Esegui"):
    path = datasets[dataset]
    if not path.exists():
        st.error(f"File non trovato: {path.name}")
    else:
        try:
            con = duckdb.connect()
            con.execute(f"CREATE VIEW {dataset} AS SELECT * FROM read_parquet('{path}')")
            result = con.sql(sql).df()
            st.dataframe(result, width="stretch", height=400)
            st.caption(f"{len(result)} righe · {len(result.columns)} colonne")
        except Exception as e:
            st.error(f"Errore: {e}")

st.markdown("---")
st.caption("Dati: MEF — 2023 · DuckDB locale · CC BY 4.0")
