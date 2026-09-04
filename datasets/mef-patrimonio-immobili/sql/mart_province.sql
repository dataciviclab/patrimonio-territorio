-- mart_province: aggregazione per provincia con metriche chiave
SELECT
    anno,
    regione_bene,
    provincia_bene,
    COUNT(*) AS totale,
    COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) AS non_utilizzati,
    ROUND(100.0 * COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) / COUNT(*), 1) AS pct_inutilizzati,
    ROUND(SUM(COALESCE(superficie_riferimento_mq, 0)), 0) AS superficie_totale_mq,
    COUNT(CASE WHEN vincoli != 'Nessuno' AND vincoli IS NOT NULL THEN 1 END) AS vincolati
FROM clean_input
GROUP BY anno, regione_bene, provincia_bene
