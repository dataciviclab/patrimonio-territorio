"""Fonti dati per la dashboard Patrimonio Pubblico Italia.

Pattern standard Lab: lab_connectors.duckdb.queries + registry.
Auto-detect locale/GCS: in locale legge da out/, su GCS da gs://.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from lab_connectors.branding import apply_branding
from lab_connectors.duckdb.queries import (
    load_mart_table as _load_mart_table,
    query_clean as _query_clean,
)

# ── Costanti dominio ─────────────────────────────────────────────────────────

PREFIX = "patrimonio_territorio/"
YEARS = [2023]
DEFAULT_YEAR = 2023

# Slugs
SLUG_IMMOBILI = "mef_patrimonio_immobili"
SLUG_DETENZIONI = "mef_patrimonio_detenzioni"
SLUG_ENTI = "mef_patrimonio_enti"


# ── Cached wrappers ──────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def query_immobili(sql: str, year: int = DEFAULT_YEAR):
    return _query_clean(SLUG_IMMOBILI, sql, [year], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def query_detenzioni(sql: str, year: int = DEFAULT_YEAR):
    return _query_clean(SLUG_DETENZIONI, sql, [year], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def query_enti(sql: str, year: int = DEFAULT_YEAR):
    return _query_clean(SLUG_ENTI, sql, [year], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(slug: str, table: str, year: int = DEFAULT_YEAR):
    return _load_mart_table(slug, table, year, prefix=PREFIX)


# ── Funzioni di dominio (cachate) ────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def kpi_immobili():
    return query_immobili("""
        SELECT
            COUNT(*) AS totale,
            COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) AS non_utilizzati,
            COUNT(CASE WHEN utilizzo_bene = 'Inutilizzabile' THEN 1 END) AS inutilizzabili,
            COUNT(CASE WHEN utilizzo_bene = 'Utilizzato direttamente' THEN 1 END) AS utilizzati,
            ROUND(SUM(COALESCE(superficie_riferimento_mq, 0)), 0) AS superficie_totale
        FROM clean_input
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def distribuzione_utilizzo():
    return query_immobili("""
        SELECT COALESCE(utilizzo_bene, 'Non specificato') AS stato, COUNT(*) AS n
        FROM clean_input GROUP BY stato ORDER BY n DESC
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def distribuzione_tipologia():
    return query_immobili("""
        SELECT tipologia_bene, COUNT(*) AS n FROM clean_input
        WHERE tipologia_bene IS NOT NULL
        GROUP BY tipologia_bene ORDER BY n DESC LIMIT 12
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def regioni_inutilizzati():
    return load_mart(SLUG_IMMOBILI, "mart_regioni")


@st.cache_data(ttl=3600, show_spinner=False)
def mappa_comuni(regione: str = None):
    where = "WHERE latitudine IS NOT NULL AND longitudine IS NOT NULL"
    if regione:
        where += f" AND regione_bene = '{regione}'"
    return query_immobili(f"""
        SELECT comune_bene, regione_bene, provincia_bene,
            ROUND(AVG(latitudine), 5) AS lat, ROUND(AVG(longitudine), 5) AS lon,
            COUNT(*) AS totale,
            COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) AS non_utilizzati,
            ROUND(100.0 * COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) / COUNT(*), 1) AS pct_inutilizzati,
            ROUND(SUM(COALESCE(superficie_riferimento_mq, 0)) / 1000, 0) AS sup_kmq,
            COUNT(CASE WHEN vincoli != 'Nessuno' AND vincoli IS NOT NULL THEN 1 END) AS vincolati,
            MODE() WITHIN GROUP (ORDER BY tipologia_bene) AS tipologia_top
        FROM clean_input {where}
        GROUP BY comune_bene, regione_bene, provincia_bene
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def immobili_comune(comune: str, provincia: str, regione: str, filtro_tipo: tuple = (), filtro_util: tuple = ()):
    where = [f"comune_bene = '{comune}'", "latitudine IS NOT NULL"]
    if filtro_tipo:
        placeholders = ", ".join(f"'{t}'" for t in filtro_tipo)
        where.append(f"tipologia_bene IN ({placeholders})")
    if filtro_util:
        placeholders = ", ".join(f"'{u}'" for u in filtro_util)
        where.append(f"utilizzo_bene IN ({placeholders})")
    where_sql = " AND ".join(where)
    return query_immobili(f"""
        SELECT latitudine AS lat, longitudine AS lon,
            id_bene, tipologia_bene, utilizzo_bene, vincoli,
            natura_giuridica_bene, indirizzo, numero_civico,
            superficie_riferimento_mq, epoca_costruzione,
            amministrazione_denominazione
        FROM clean_input WHERE {where_sql}
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def kpi_comune(comune: str):
    return query_immobili(f"""
        SELECT COUNT(*) AS totale,
            COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) AS non_utilizzati,
            COUNT(CASE WHEN utilizzo_bene = 'Inutilizzabile' THEN 1 END) AS inutilizzabili,
            ROUND(SUM(COALESCE(superficie_riferimento_mq, 0)), 0) AS superficie,
            COUNT(CASE WHEN vincoli != 'Nessuno' AND vincoli IS NOT NULL THEN 1 END) AS vincolati
        FROM clean_input WHERE comune_bene = '{comune}'
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def kpi_detenzioni():
    return query_detenzioni("""
        SELECT COUNT(*) AS totale,
            COUNT(CASE WHEN canone_annuale > 0 THEN 1 END) AS con_canone,
            ROUND(SUM(COALESCE(canone_annuale, 0)), 0) AS totale_canoni,
            ROUND(AVG(CASE WHEN canone_annuale > 0 THEN canone_annuale END), 0) AS media_canone
        FROM clean_input
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def detenzioni_per_tipo():
    return load_mart(SLUG_DETENZIONI, "mart_tipo_detenzione")


@st.cache_data(ttl=3600, show_spinner=False)
def detenzioni_per_finalita():
    return query_detenzioni("""
        SELECT COALESCE(finalita_pf, 'Non specificata') AS finalita,
            COUNT(*) AS n, ROUND(SUM(canone_annuale), 0) AS canone_totale
        FROM clean_input GROUP BY finalita ORDER BY n DESC
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def detenzioni_soggetti():
    return query_detenzioni("""
        SELECT CASE WHEN soggetto_ricevente_pa THEN 'PA' ELSE 'Non-PA' END AS tipo_pa,
            COUNT(*) AS n FROM clean_input GROUP BY tipo_pa
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def distribuzione_vincoli():
    return query_immobili("""
        SELECT vincoli, COUNT(*) AS n FROM clean_input
        WHERE vincoli IS NOT NULL GROUP BY vincoli ORDER BY n DESC
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def distribuzione_natura():
    return query_immobili("""
        SELECT natura_giuridica_bene, COUNT(*) AS n FROM clean_input
        WHERE natura_giuridica_bene IS NOT NULL
        GROUP BY natura_giuridica_bene ORDER BY n DESC
    """)


# ── Formattazione ────────────────────────────────────────────────────────────

def fmt_num(val):
    if val is None or val != val:
        return "-"
    return f"{int(val):,}".replace(",", ".")


def fmt_eur(val):
    if val is None or val != val:
        return "-"
    if abs(val) >= 1e9:
        return f"{val/1e9:.1f} mld EUR"
    if abs(val) >= 1e6:
        return f"{val/1e6:.1f} M EUR"
    if abs(val) >= 1e3:
        return f"{val/1e3:.0f} kEUR"
    return f"{val:.0f} EUR"


def fmt_mq(val):
    if val is None or val != val:
        return "-"
    if abs(val) >= 1e6:
        return f"{val/1e6:.1f} M mq"
    if abs(val) >= 1e3:
        return f"{val/1e3:.0f} k mq"
    return f"{val:.0f} mq"
