# Patrimonio Pubblico Italia — Mappa del patrimonio immobiliare delle PA

**3,25 milioni di immobili pubblici, 100% georeferenziati. Quanto è utilizzato, quanto è abbandonato?**

Censimento immobiliare delle pubbliche amministrazioni italiane: dati del MEF
Dipartimento dell'Economia, arricchiti con coordinate geografiche, vincoli, destinazione d'uso
e informazioni sulle detenzioni a favore di terzi.

## Cosa contiene

| | Immobili | Detenzioni | Enti |
|---|---|---|---|
| **Righe** | **3.257.044** | **564.003** | **11.326** |
| **Periodo** | 2022-2023 | 2022-2023 | 2022-2023 |
| **Georeferenziazione** | 100% | via id_bene | per ente |
| **Coordinate** | lat/long (WGS84) | — | — |

## Numeri chiave (2023)

- **21%** degli immobili è **non utilizzato** (688.184 beni)
- **Basilicata** ha il 46% di immobili inutilizzati, **Emilia Romagna** solo l'8%
- **€1,97 miliardi** di canoni incassati dalle detenzioni
- **360 km²** di superficie totale

## Esempi di domande

- Quali regioni hanno la percentuale più alta di immobili pubblici inutilizzati?
- Quanto reddito generano le detenzioni a favore di terzi?
- Quali tipi di bene sono più collassati?
- Quanti immobili sono vincolati e non utilizzati?

## Dashboard

Streamlit interattiva con 5 pagine:

- **Panoramica** — KPI nazionali, distribuzione utilizzo, top regioni
- **Mappa** — Density map degli immobili con filtri
- **Territorio** — Choropleth regioni, ranking, dettaglio province
- **Detenzioni** — Canoni, finalità, soggetti riceventi
- **Query SQL** — Query libera su tutti i dataset

## Quickstart

```bash
# Pipeline
pip install -e ".[pipeline]"
make run

# Dashboard
cd dashboard && streamlit run app.py
```

## Fonti

| Fonte | Dati | Licenza |
|---|---|---|
| MEF — Censimento immobili pubblici PA | Immobili, detenzioni, enti | CC BY 4.0 |

## Licenza

- **Dati**: CC BY 4.0 (MEF)
- **Codice**: MIT
