-- mart_regioni: aggregazione per regione con metriche chiave per la dashboard
SELECT
    anno,
    regione_bene,
    COUNT(*) AS totale,
    COUNT(CASE WHEN utilizzo_bene = 'Utilizzato direttamente' THEN 1 END) AS utilizzati,
    COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) AS non_utilizzati,
    COUNT(CASE WHEN utilizzo_bene = 'Inutilizzabile' THEN 1 END) AS inutilizzabili,
    COUNT(CASE WHEN utilizzo_bene = 'In ristrutturazione/manutenzione' THEN 1 END) AS in_ristrutturazione,
    ROUND(100.0 * COUNT(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN 1 END) / COUNT(*), 1) AS pct_inutilizzati,
    ROUND(SUM(COALESCE(superficie_riferimento_mq, 0)), 0) AS superficie_totale_mq,
    ROUND(SUM(CASE WHEN utilizzo_bene = 'Non utilizzato' THEN COALESCE(superficie_riferimento_mq, 0) ELSE 0 END), 0) AS superficie_inutilizzata_mq,
    COUNT(CASE WHEN natura_giuridica_bene = 'Demanio' THEN 1 END) AS demanio,
    COUNT(CASE WHEN natura_giuridica_bene = 'Patrimonio indisponibile' THEN 1 END) AS patrimonio_indisponibile,
    COUNT(CASE WHEN natura_giuridica_bene = 'Patrimonio disponibile' THEN 1 END) AS patrimonio_disponibile,
    COUNT(CASE WHEN vincoli != 'Nessuno' AND vincoli IS NOT NULL THEN 1 END) AS vincolati
FROM clean_input
GROUP BY anno, regione_bene
