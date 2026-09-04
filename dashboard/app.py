#!/usr/bin/env python3
"""
Patrimonio Pubblico Italia · Dashboard Streamlit
Mappa del patrimonio immobiliare pubblico italiano: 3,2 milioni di immobili, 100% georeferenziati.
"""

import streamlit as st

st.set_page_config(
    page_title="Patrimonio Pubblico Italia",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from lab_connectors.branding import apply_branding

apply_branding(
    repo_name="patrimonio-territorio",
    repo_url="https://github.com/dataciviclab/patrimonio-territorio",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Mappa": [
        st.Page("pages/02_Mappa.py", title="Mappa immobili", icon="🗺️"),
        st.Page("pages/03_Territorio.py", title="Territorio", icon="🏘️"),
    ],
    "Analisi": [
        st.Page("pages/04_Detenzioni.py", title="Detenzioni & Canoni", icon="💰"),
    ],
    "Strumenti": [
        st.Page("pages/05_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

st.sidebar.caption("Dati: MEF Dipartimento Economia — Censimento immobili pubblici PA")

pg.run()
