-- mart_tipo_detenzione: aggregazione per tipo di detenzione con canoni
SELECT
    anno,
    tipo_detenzione_terzi,
    COUNT(*) AS n,
    ROUND(SUM(COALESCE(canone_annuale, 0)), 0) AS canone_totale,
    ROUND(AVG(CASE WHEN canone_annuale > 0 THEN canone_annuale END), 0) AS canone_medio,
    COUNT(CASE WHEN canone_annuale > 0 THEN 1 END) AS con_canone,
    COUNT(CASE WHEN soggetto_ricevente_pa THEN 1 END) AS riceventi_pa,
    COUNT(CASE WHEN NOT soggetto_ricevente_pa THEN 1 END) AS riceventi_non_pa
FROM clean_input
GROUP BY anno, tipo_detenzione_terzi
